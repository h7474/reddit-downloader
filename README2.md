# Reddit Subreddit Post & Comment Downloader (Date Range)

This Python script downloads all posts made within the `r/selfhosted` subreddit during a specified date range. It also fetches all comments under each of those posts, along with upvote counts for both posts and comments. The collected data is saved into a structured JSON file.

## Features

- Fetches all posts from `r/selfhosted` created within a user-specified start and end date.
- Fetches all comments (including nested comments) for each relevant post.
- Retrieves post details: ID, title, author, URL, permalink, creation time, score (upvotes), upvote ratio, selftext, and comment count.
- Retrieves comment details: ID, author, body, score (upvotes), creation time, and permalink.
- Saves data in a well-structured JSON format.
- Configurable via command-line arguments (for date range and output file), environment variables, or `praw.ini` (for credentials).

## Requirements

- Python 3.6+
- PRAW (Python Reddit API Wrapper)
- Reddit Account
- Reddit API Credentials (Script App)

## Setup

### 1. Install PRAW

If you don't have PRAW installed, open your terminal or command prompt and run:

```bash
pip install praw
```

### 2. Get Reddit API Credentials

You need to register a 'script' application on Reddit to get API credentials:

1.  Log in to your Reddit account.
2.  Go to the Reddit apps page: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
3.  Scroll down and click the "are you a developer? create an app..." button.
4.  Fill out the form:
    *   **Name:** Give your app a name (e.g., `Selfhosted DateRange Downloader`).
    *   **Type:** Select **`script`**.
    *   **Description:** (Optional) Add a brief description.
    *   **About URL:** (Optional)
    *   **Redirect URI:** Enter `http://localhost:8080` (PRAW requires this for script apps, even though it's not strictly used in this script's authentication flow).
5.  Click "create app".
6.  You will now see your app listed. Note down the following:
    *   **Client ID:** The string of characters listed under "personal use script".
    *   **Client Secret:** The string of characters listed next to `secret`.

### 3. Configure Credentials

You need to provide your Reddit account details and the API credentials (from Step 2) to the script. **Avoid hardcoding credentials directly in the script if possible.** Here are the recommended methods:

**Method A: Environment Variables (Recommended)**

Set the following environment variables in your system:

```bash
export REDDIT_CLIENT_ID='YOUR_CLIENT_ID'
export REDDIT_CLIENT_SECRET='YOUR_CLIENT_SECRET'
export REDDIT_USERNAME='YOUR_REDDIT_USERNAME'
export REDDIT_PASSWORD='YOUR_REDDIT_PASSWORD'
export REDDIT_USER_AGENT='Python:SelfhostedDownloaderDateRange:v1.2 (by /u/YOUR_REDDIT_USERNAME)' # Customize this!
```

Replace the placeholder values with your actual credentials. Remember to customize the `REDDIT_USER_AGENT` string, replacing `YOUR_REDDIT_USERNAME` with your Reddit username.

**Method B: `praw.ini` File**

Create a file named `praw.ini` in the same directory as the script (`reddit_subreddit_downloader_daterange.py`) or in your user's configuration directory (e.g., `~/.config/praw.ini` on Linux/macOS, `%APPDATA%\praw.ini` on Windows).

Add the following content:

```ini
[DEFAULT]
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
username=YOUR_REDDIT_USERNAME
password=YOUR_REDDIT_PASSWORD
user_agent=Python:SelfhostedDownloaderDateRange:v1.2 (by /u/YOUR_REDDIT_USERNAME)
```

Replace the placeholder values. PRAW will automatically detect and use this file.

**Method C: Edit the Script (Least Secure)**

If you choose to edit the script directly (like we did for testing), open `reddit_subreddit_downloader_daterange.py` and modify the configuration section near the top:

```python
# --- Configuration --- 
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
USERNAME = "YOUR_REDDIT_USERNAME"
PASSWORD = "YOUR_REDDIT_PASSWORD"
USER_AGENT = "Python:SelfhostedDownloaderDateRange:v1.2 (by /u/YOUR_REDDIT_USERNAME)" # Customize!
# --- End Configuration ---
```

Replace the placeholder values. Be careful not to share the script with your credentials embedded.

### 4. User Agent

Make sure your User Agent string is unique and descriptive, including your Reddit username as recommended by Reddit's API terms. The examples above follow the suggested format.

## Usage

Open your terminal or command prompt, navigate to the directory where you saved `reddit_subreddit_downloader_daterange.py`, and run the script using Python, providing the start and end dates:

```bash
python reddit_subreddit_downloader_daterange.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

**Required Arguments:**

*   `--start-date YYYY-MM-DD`: The first date (inclusive) to fetch posts from.
*   `--end-date YYYY-MM-DD`: The last date (inclusive) to fetch posts from. Posts up to 23:59:59 UTC on this day will be included.

**Optional Arguments:**

*   `-o <filename>` or `--output <filename>`: Specify a custom name for the output JSON file. If omitted, it defaults to `selfhosted_<start_date>_to_<end_date>_data.json`.

**Example:**

To download data for posts between April 15th, 2025 and April 20th, 2025 (inclusive) and save it to `selfhosted_apr15_apr20.json`:

```bash
python reddit_subreddit_downloader_daterange.py --start-date 2025-04-15 --end-date 2025-04-20 -o selfhosted_apr15_apr20.json
```

The script will authenticate, fetch the data within the specified date range, print progress messages to the console, and save the results in the specified JSON file.

## Output Format

The output JSON file will have the following structure:

```json
{
    "subreddit": "selfhosted",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "start_timestamp_utc": 1746057600.0,
    "end_timestamp_utc": 1746230399.0,
    "download_time": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
    "posts": [
        {
            "id": "post_id",
            "title": "Post Title",
            "author": "post_author_username",
            "url": "post_url",
            "permalink": "full_reddit_link_to_post",
            "created_utc": 1678886400.0,
            "score": 123,
            "upvote_ratio": 0.95,
            "selftext": "Body text of the post...",
            "num_comments": 50,
            "comments": [
                {
                    "id": "comment_id",
                    "author": "comment_author_username",
                    "body": "Text of the comment...",
                    "score": 45,
                    "created_utc": 1678887000.0,
                    "permalink": "full_reddit_link_to_comment"
                },
                // ... more comments
            ]
        },
        // ... more posts
    ]
}
```

## Notes

*   Fetching posts and comments over a large date range can take a significant amount of time and involves many API requests. Reddit imposes rate limits, but PRAW handles basic rate limiting automatically. Be patient while the script runs.
*   The resulting JSON file can be quite large depending on the date range and subreddit activity.
*   Ensure your credentials are kept secure, especially if you modify the script directly.

