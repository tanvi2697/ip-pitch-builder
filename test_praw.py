from dotenv import load_dotenv
load_dotenv(override=True)  # <— this forces .env reload

import praw
import os

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

try:
    for post in reddit.subreddit("tifu").hot(limit=3):
        print("✅ SUCCESS:", post.title)
except Exception as e:
    print("❌ ERROR:", e)
