import os
import sys
import subprocess

# Check if required packages are installed
required_packages = [
    "streamlit",
    "pandas",
    "plotly",
    "openai",
    "requests",
    "python-dotenv",
    "beautifulsoup4",
    "lxml",
    "reportlab",
    "praw"
]

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"Installing {package}...")
        install_package(package)

# Run the actual app
import app 