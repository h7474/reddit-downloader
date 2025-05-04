#!/usr/bin/env python3
"""
Downloads all posts from r/selfhosted created within the last month,
along with comments and upvotes for both posts and comments.
Saves the data to a JSON file.
"""

import praw
import json
import argparse
import os
import sys
import time
from datetime import datetime, timedelta

# --- Configuration (Using credentials provided by user for testing) ---
# WARNING: Hardcoding credentials is a security risk. Consider using
# environment variables or a praw.ini file for regular use.
# See: https://praw.readthedocs.io/en/stable/getting_started/configuration.html
CLIENT_ID = "boS5Qjj6PoMuhozlNCWJRg"
CLIENT_SECRET = "SIB1AQw8zDd7RYWGuHna7g0JQDieow"
USERNAME = "scrypts94"
PASSWORD = "90076650171"
USER_AGENT = "Python:SelfhostedDownloader:v1.1 (by /u/scrypts94)" # Updated User Agent
# --- End Configuration ---

SUBREDDIT_NAME = "selfhosted"
TIME_PERIOD_DAYS = 30 # Download posts from the last 30 days

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

def fetch_subreddit_data(reddit, output_file):
    """Fetches posts and comments from r/selfhosted within the last month."""
    print(f"Fetching posts from r/{SUBREDDIT_NAME} created in the last {TIME_PERIOD_DAYS} days...")
    subreddit_data = {
        "subreddit": SUBREDDIT_NAME,
        "time_period_days": TIME_PERIOD_DAYS,
        "download_time": datetime.utcnow().isoformat() + "Z",
        "posts": []
    }
    post_count = 0
    comment_count = 0
    cutoff_time = time.time() - (TIME_PERIOD_DAYS * 24 * 60 * 60)

    try:
        subreddit = reddit.subreddit(SUBREDDIT_NAME)

        # Fetch new submissions from the subreddit
        for submission in subreddit.new(limit=None): # Fetch potentially many, filter by date
            if submission.created_utc < cutoff_time:
                print(f"Reached posts older than {TIME_PERIOD_DAYS} days. Stopping search.")
                break # Stop searching once posts are too old

            post_count += 1
            print(f"  Processing post {post_count}: {submission.id} (Created: {datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d')}) - \"{submission.title[:50]}...\"")
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

            subreddit_data["posts"].append(post_info)
            print(f"    Found {num_fetched_comments} comments.")

        print(f"\nFinished fetching. Found {post_count} posts and {comment_count} comments in total within the time period.")

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

def main():
    """Main function to parse arguments and run the downloader."""
    parser = argparse.ArgumentParser(description=f"Download posts and comments from r/{SUBREDDIT_NAME} created in the last {TIME_PERIOD_DAYS} days.")
    parser.add_argument("-o", "--output", default=f"{SUBREDDIT_NAME}_last_{TIME_PERIOD_DAYS}_days_data.json", help=f"Output JSON file name. Defaults to {SUBREDDIT_NAME}_last_{TIME_PERIOD_DAYS}_days_data.json")

    args = parser.parse_args()
    output_file = args.output

    reddit = authenticate_reddit()
    fetch_subreddit_data(reddit, output_file)

if __name__ == "__main__":
    main()

