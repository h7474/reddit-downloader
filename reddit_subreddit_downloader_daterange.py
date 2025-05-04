#!/usr/bin/env python3
"""
Downloads all posts from r/selfhosted created within a specified date range,
along with comments and upvotes for both posts and comments.
Saves the data to a JSON file.
"""

import praw
import json
import argparse
import os
import sys
import time
from datetime import datetime, timezone

# --- Configuration (Using credentials provided by user for testing) ---
# WARNING: Hardcoding credentials is a security risk. Consider using
# environment variables or a praw.ini file for regular use.
# See: https://praw.readthedocs.io/en/stable/getting_started/configuration.html
CLIENT_ID = "boS5Qjj6PoMuhozlNCWJRg"
CLIENT_SECRET = "SIB1AQw8zDd7RYWGuHna7g0JQDieow"
USERNAME = "scrypts94"
PASSWORD = "90076650171"
USER_AGENT = "Python:SelfhostedDownloaderDateRange:v1.2 (by /u/scrypts94)" # Updated User Agent
# --- End Configuration ---

SUBREDDIT_NAME = "selfhosted"

def authenticate_reddit():
    """Authenticates with Reddit using PRAW."""
    print("Authenticating with Reddit...")
    try:
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            password=PASSWORD,
            user_agent=USER_AGENT,
            username=USERNAME,
        )
        # Verify authentication
        print(f"Authenticated as: {reddit.user.me()}")
        return reddit
    except Exception as e:
        print(f"Error during authentication: {e}", file=sys.stderr)
        print("Please ensure your credentials (CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD, USER_AGENT) are correct.", file=sys.stderr)
        print("You might need to register a 'script' application on Reddit: https://www.reddit.com/prefs/apps", file=sys.stderr)
        sys.exit(1)

def fetch_subreddit_data(reddit, start_timestamp, end_timestamp, output_file):
    """Fetches posts and comments from r/selfhosted within the specified date range."""
    start_dt_str = datetime.utcfromtimestamp(start_timestamp).strftime('%Y-%m-%d')
    end_dt_str = datetime.utcfromtimestamp(end_timestamp).strftime('%Y-%m-%d')
    print(f"Fetching posts from r/{SUBREDDIT_NAME} created between {start_dt_str} and {end_dt_str}...")
    subreddit_data = {
        "subreddit": SUBREDDIT_NAME,
        "start_date": start_dt_str,
        "end_date": end_dt_str,
        "start_timestamp_utc": start_timestamp,
        "end_timestamp_utc": end_timestamp,
        "download_time": datetime.utcnow().isoformat() + "Z",
        "posts": []
    }
    post_count = 0
    comment_count = 0

    try:
        subreddit = reddit.subreddit(SUBREDDIT_NAME)

        # Fetch new submissions from the subreddit
        # We fetch in reverse chronological order and stop when posts are too old
        for submission in subreddit.new(limit=None):
            # Stop if the post is older than the start date
            if submission.created_utc < start_timestamp:
                print(f"Reached posts older than {start_dt_str}. Stopping search.")
                break

            # Skip if the post is newer than the end date (shouldn't happen with .new() but good practice)
            if submission.created_utc > end_timestamp:
                continue

            # Process posts within the date range
            post_count += 1
            print(f"  Processing post {post_count}: {submission.id} (Created: {datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')}) - \"{submission.title[:50]}...\"")
            post_info = {
                "id": submission.id,
                "title": submission.title,
                "author": str(submission.author),
                "url": submission.url,
                "permalink": f"https://www.reddit.com{submission.permalink}",
                "created_utc": submission.created_utc,
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "selftext": submission.selftext,
                "num_comments": submission.num_comments,
                "comments": []
            }

            # Fetch comments for the submission
            try:
                submission.comments.replace_more(limit=None) # Expand all MoreComments objects
                num_fetched_comments = 0
                for comment in submission.comments.list():
                    comment_count += 1
                    num_fetched_comments += 1
                    comment_info = {
                        "id": comment.id,
                        "author": str(comment.author), # Handle potential None author
                        "body": comment.body,
                        "score": comment.score,
                        "created_utc": comment.created_utc,
                        "permalink": f"https://www.reddit.com{comment.permalink}"
                    }
                    post_info["comments"].append(comment_info)
                print(f"    Found {num_fetched_comments} comments.")
            except Exception as comment_e:
                print(f"    Error fetching comments for post {submission.id}: {comment_e}", file=sys.stderr)
                # Continue to next post even if comments fail for one

            subreddit_data["posts"].append(post_info)

        print(f"\nFinished fetching. Found {post_count} posts and {comment_count} comments in total within the specified date range.")

        # Save data to JSON file
        print(f"Saving data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(subreddit_data, f, indent=4, ensure_ascii=False)
        print("Data saved successfully.")

    except Exception as e:
        print(f"An error occurred while fetching data: {e}", file=sys.stderr)
        # Optionally save partial data if needed
        # with open(output_file + ".partial", 'w', encoding='utf-8') as f:
        #     json.dump(subreddit_data, f, indent=4, ensure_ascii=False)
        # print(f"Partial data saved to {output_file}.partial", file=sys.stderr)

def valid_date(s):
    """Convert YYYY-MM-DD string to UTC timestamp at start of day."""
    try:
        # Assume input is UTC date, get timestamp for start of that day (00:00:00 UTC)
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        msg = f"Not a valid date: '{s}'. Expected format: YYYY-MM-DD."
        raise argparse.ArgumentTypeError(msg)

def main():
    """Main function to parse arguments and run the downloader."""
    parser = argparse.ArgumentParser(description=f"Download posts and comments from r/{SUBREDDIT_NAME} within a specified date range.")
    parser.add_argument("--start-date", required=True, type=valid_date, help="Start date (inclusive) in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, type=valid_date, help="End date (inclusive) in YYYY-MM-DD format. Posts up to 23:59:59 UTC on this day will be included.")
    parser.add_argument("-o", "--output", default=None, help="Output JSON file name. Defaults to <subreddit>_<start_date>_to_<end_date>_data.json")

    args = parser.parse_args()

    start_timestamp = args.start_date
    # Add almost a full day to the end timestamp to include the entire end date
    end_timestamp = args.end_date + (24 * 60 * 60 - 1)

    if start_timestamp > end_timestamp:
        print("Error: Start date cannot be after end date.", file=sys.stderr)
        sys.exit(1)

    start_dt_str = datetime.utcfromtimestamp(start_timestamp).strftime('%Y-%m-%d')
    end_dt_str = datetime.utcfromtimestamp(args.end_date).strftime('%Y-%m-%d') # Use original end_date for filename

    output_file = args.output if args.output else f"{SUBREDDIT_NAME}_{start_dt_str}_to_{end_dt_str}_data.json"

    reddit = authenticate_reddit()
    fetch_subreddit_data(reddit, start_timestamp, end_timestamp, output_file)

if __name__ == "__main__":
    main()

