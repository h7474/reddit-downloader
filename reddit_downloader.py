#!/usr/bin/env python3
"""
Downloads all posts by a specific user in r/selfhosted,
along with comments and upvotes for both posts and comments.
Saves the data to a JSON file.
"""

import praw
import json
import argparse
import os
import sys
from datetime import datetime

# --- Configuration (Replace with your credentials or use environment variables/praw.ini) ---
# It is STRONGLY recommended to use environment variables or a praw.ini file
# instead of hardcoding credentials here.
# See: https://praw.readthedocs.io/en/stable/getting_started/configuration.html
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "YOUR_CLIENT_ID") # Replace or set env var
CLIENT_ID = "boS5Qjj6PoMuhozlNCWJRg"

CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET") # Replace or set env var
CLIENT_SECRET = "SIB1AQw8zDd7RYWGuHna7g0JQDieow"

USERNAME = os.environ.get("REDDIT_USERNAME", "YOUR_REDDIT_USERNAME") # Replace or set env var
USERNAME = "scrypts94"

PASSWORD = os.environ.get("REDDIT_PASSWORD", "YOUR_REDDIT_PASSWORD") # Replace or set env var
PASSWORD = "90076650171"

USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "Reddit Downloader Script by YOUR_USERNAME") # Replace YOUR_USERNAME
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

def fetch_user_data(reddit, target_username, output_file):
    """Fetches posts and comments for the target user in r/selfhosted."""
    print(f"Fetching data for user: u/{target_username} in r/{SUBREDDIT_NAME}...")
    user_data = {
        "username": target_username,
        "subreddit": SUBREDDIT_NAME,
        "download_time": datetime.utcnow().isoformat() + "Z",
        "posts": []
    }
    post_count = 0
    comment_count = 0

    try:
        redditor = reddit.redditor(target_username)
        subreddit = reddit.subreddit(SUBREDDIT_NAME)

        # Fetch submissions (posts) by the user in the specified subreddit
        for submission in redditor.submissions.new(limit=None): # Fetch all submissions
            if submission.subreddit.display_name.lower() == SUBREDDIT_NAME.lower():
                post_count += 1
                print(f"  Processing post {post_count}: {submission.id} - \"{submission.title[:50]}...\"")
                post_info = {
                    "id": submission.id,
                    "title": submission.title,
                    "url": submission.url,
                    "permalink": f"https://www.reddit.com{submission.permalink}",
                    "created_utc": submission.created_utc,
                    "score": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "selftext": submission.selftext,
                    "comments": []
                }

                # Fetch comments for the submission
                submission.comments.replace_more(limit=None) # Expand all MoreComments objects
                for comment in submission.comments.list():
                    comment_count += 1
                    comment_info = {
                        "id": comment.id,
                        "author": str(comment.author), # Handle potential None author
                        "body": comment.body,
                        "score": comment.score,
                        "created_utc": comment.created_utc,
                        "permalink": f"https://www.reddit.com{comment.permalink}"
                    }
                    post_info["comments"].append(comment_info)

                user_data["posts"].append(post_info)
                print(f"    Found {len(post_info['comments'])} comments.")

        print(f"\nFinished fetching. Found {post_count} posts and {comment_count} comments in total.")

        # Save data to JSON file
        print(f"Saving data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=4, ensure_ascii=False)
        print("Data saved successfully.")

    except Exception as e:
        print(f"An error occurred while fetching data: {e}", file=sys.stderr)
        # Optionally save partial data if needed
        # with open(output_file + ".partial", 'w', encoding='utf-8') as f:
        #     json.dump(user_data, f, indent=4, ensure_ascii=False)
        # print(f"Partial data saved to {output_file}.partial", file=sys.stderr)

def main():
    """Main function to parse arguments and run the downloader."""
    parser = argparse.ArgumentParser(description=f"Download posts and comments for a Reddit user from r/{SUBREDDIT_NAME}.")
    parser.add_argument("username", help="The Reddit username to fetch data for.")
    parser.add_argument("-o", "--output", default=None, help="Output JSON file name. Defaults to <username>_selfhosted_data.json")

    args = parser.parse_args()

    target_username = args.username
    output_file = args.output if args.output else f"{target_username}_selfhosted_data.json"

    # Basic credential check (encourage better methods)
    if CLIENT_ID == "YOUR_CLIENT_ID" or CLIENT_SECRET == "YOUR_CLIENT_SECRET" or \
       USERNAME == "YOUR_REDDIT_USERNAME" or PASSWORD == "YOUR_REDDIT_PASSWORD" or \
       USER_AGENT == "Reddit Downloader Script by YOUR_USERNAME":
        print("WARNING: Default credentials detected. Please configure your Reddit API credentials", file=sys.stderr)
        print("         either in the script, environment variables, or a praw.ini file.", file=sys.stderr)
        # Decide if you want to exit or proceed with potentially invalid credentials
        # sys.exit(1)

    reddit = authenticate_reddit()
    fetch_user_data(reddit, target_username, output_file)

if __name__ == "__main__":
    main()

