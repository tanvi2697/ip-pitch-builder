#!/usr/bin/env python3
"""
Launcher script for IP Pitch Builder
"""
import os
import subprocess
import sys
import platform

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import streamlit
        import openai
        import pandas
        import plotly
        print("✅ All core dependencies found!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run 'pip install -r requirements.txt' to install dependencies")
        return False

def check_api_keys():
    """Check if required API keys are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    warnings = []
    
    if not os.environ.get("OPENAI_API_KEY"):
        warnings.append("⚠️ OPENAI_API_KEY not found in environment or .env file")
        warnings.append("   Some AI features will be limited to demo mode")
    
    if not os.environ.get("REDDIT_CLIENT_ID") or not os.environ.get("REDDIT_CLIENT_SECRET"):
        warnings.append("⚠️ Reddit API credentials not found in environment or .env file")
        warnings.append("   You'll need to enter them in the app to scrape Reddit content")
    
    if warnings:
        print("\n".join(warnings))
        print("You can add these to a .env file in the project root")
        return False
    else:
        print("✅ API keys found!")
        return True

def launch_app():
    """Launch the Streamlit app"""
    print("🚀 Launching IP Pitch Builder...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to launch application")
        return False
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("IP Pitch Builder - Launcher")
    print("=" * 60)
    
    # Print system info
    print(f"🖥️  System: {platform.system()} {platform.version()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("-" * 60)
    
    # Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        sys.exit(1)
    
    # Check API keys
    keys_ok = check_api_keys()
    # Continue even if keys are missing
    
    # Launch app
    launch_app() 