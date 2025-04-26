# IP Pitch Builder

A Streamlit application that helps users find high-potential movie and TV series ideas from Reddit and Wattpad, and generate professional pitch materials for streaming platforms and production companies.

## Features

- **Content Discovery**: Find viral stories from Reddit and Wattpad with untapped adaptation potential
- **AI-Powered Analysis**: Score adaptation potential and recommend optimal formats using GPT-4o
- **Complete Pitch Generation**: Create compelling pitch decks, character profiles, and plot summaries
- **Visual Assets**: Generate movie posters and visual concepts with DALL-E 3
- **Cast Suggestions**: Get AI-suggested actors who would be perfect for your adaptation
- **Alternate Endings**: Explore different narrative possibilities for your adaptation
- **Teaser Trailer Scripts**: Create compelling teaser trailer scripts to pitch your concept
- **Export to PDF**: Compile all materials into a professional pitch deck PDF

## Setup Instructions

### Prerequisites

- Python 3.9+ installed
- OpenAI API key (for GPT-4o and DALL-E 3 integration)
- Reddit API credentials (for Reddit content scraping)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/tanvi2697/reddit-story-miner.git
   cd reddit-story-miner
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT="story_selector:v1.0 (by /u/your_username)"
   ```

### Running the Application

You can run the application using our convenient launcher script:
```
python run.py
```

Or directly start the Streamlit app:
```
streamlit run app.py
```

The application will be available at http://localhost:8501 in your web browser.

## Local Deployment Guide

To deploy this application locally for others to access on your network:

1. Ensure you have all prerequisites installed and configured
2. Run the application with the following command:
   ```
   streamlit run app.py --server.address=0.0.0.0 --server.port=8501
   ```
3. The application will be accessible from other devices on your network using your machine's IP address with port 8501
   ```
   http://YOUR_IP_ADDRESS:8501
   ```

## Deploying to Streamlit Community Cloud

You can deploy this application for free on Streamlit Community Cloud:

1. Ensure your code is pushed to a GitHub repository
2. Visit [Streamlit Community Cloud](https://share.streamlit.io/)
3. Sign in with GitHub
4. Click "New app"
5. Select this repository, main branch, and streamlit_app.py as the entry point
6. Enter your secrets (OpenAI API key and Reddit credentials) in the Advanced Settings
7. Click "Deploy"

After deployment, you'll receive a public URL for your app that anyone can access. The app will automatically update whenever you push changes to your GitHub repository.

## Usage Guide

1. **Discover Content**: 
   - Select a content source (Reddit or Wattpad)
   - Configure filters to find interesting stories
   - Analyze adaptation potential

2. **Develop Adaptation**:
   - Generate pitch deck, character profiles, and plot synopsis
   - Create movie posters and teaser trailer scripts
   - Explore alternate endings

3. **Market Your Blockbuster**:
   - Get market analysis and cast suggestions
   - Export everything to a professional PDF pitch deck

## Dependencies

- streamlit: Web application framework
- openai: OpenAI API client for GPT-4o and DALL-E
- pandas: Data manipulation
- plotly: Interactive visualizations
- reportlab: PDF generation
- praw: Reddit API wrapper
- beautifulsoup4: Web scraping for Wattpad
- python-dotenv: Environment variable management

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are correctly installed:
   ```
   pip install -r requirements.txt
   ```

2. Verify your API keys in the `.env` file are correct

3. For module errors, try installing the specific missing package:
   ```
   pip install <package_name>
   ```

4. If the application crashes, check the logs for detailed error information 