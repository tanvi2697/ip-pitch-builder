import praw
import pandas as pd
from datetime import datetime
import time
import re

def fetch_reddit_posts(subreddit, time_filter="week", limit=10, client_id=None, 
                       client_secret=None, user_agent=None, min_score=1000, min_comments=100):
    """
    Fetches posts from a specific subreddit based on given criteria
    
    Args:
        subreddit (str): Subreddit name to fetch posts from
        time_filter (str): Time filter for posts ('day', 'week', 'month', 'year', 'all')
        limit (int): Number of posts to fetch
        client_id (str): Reddit API client ID
        client_secret (str): Reddit API client secret
        user_agent (str): Reddit API user agent
        min_score (int): Minimum score (upvotes) for posts
        min_comments (int): Minimum number of comments for posts
        
    Returns:
        list: List of posts as dictionaries or error message
    """
    try:
        # Check if credentials are provided
        if not client_id or not client_secret:
            print(f"Missing Reddit credentials. client_id exists: {bool(client_id)}, client_secret exists: {bool(client_secret)}")
            return "Missing Reddit API credentials. Please provide both client_id and client_secret."
            
        # Clean up credentials (remove whitespace)
        client_id = client_id.strip() if client_id else ""
        client_secret = client_secret.strip() if client_secret else ""
        user_agent = user_agent.strip() if user_agent else "python:reddit-adaptation-analyzer:v1.0"
        
        print(f"Connecting to Reddit API with client_id: {client_id[:4]}... and user_agent: {user_agent}")
        
        # Initialize the Reddit API client
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Fetch the subreddit
        sub = reddit.subreddit(subreddit)
        
        # Fetch posts
        posts = []
        for post in sub.top(time_filter=time_filter, limit=limit*2):  # Fetch more to filter
            # Skip posts that don't meet criteria
            if post.score < min_score or post.num_comments < min_comments:
                continue
                
            # Skip non-text posts or deleted/removed content
            if not post.is_self or post.selftext in ['[removed]', '[deleted]', '']:
                continue
                
            # Extract data from the post
            post_data = {
                'id': post.id,
                'title': post.title,
                'selftext': clean_text(post.selftext),
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d'),
                'subreddit': subreddit,
                'permalink': post.permalink,
                'url': post.url
            }
            
            posts.append(post_data)
            
            # Stop if we have enough posts
            if len(posts) >= limit:
                break
                
        return posts
    
    except Exception as e:
        error_message = str(e)
        print(f"Reddit API Error: {error_message}")
        
        # Provide more helpful error messages based on common issues
        if "invalid_grant" in error_message.lower() or "unauthorized" in error_message.lower():
            return "Error: Invalid Reddit API credentials. Please check your client ID and client secret."
        elif "permission" in error_message.lower():
            return "Error: Insufficient permissions with the provided Reddit API credentials."
        elif "rate limit" in error_message.lower():
            return "Error: Reddit API rate limit exceeded. Please try again later."
        elif "connection" in error_message.lower() or "timeout" in error_message.lower():
            return "Error: Connection issue with Reddit API. Please check your internet connection."
        else:
            return f"Error connecting to Reddit: {error_message}"

def clean_text(text):
    """Cleans and formats Reddit post text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove Reddit formatting
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Remove links
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    
    # Truncate if too long (max ~2000 tokens)
    max_length = 8000
    if len(text) > max_length:
        text = text[:max_length] + "..."
        
    return text
