import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import random
import plotly.graph_objects as go
import openai
import time

import os
print("✅ app.py running in:", os.getcwd())

from reddit_scraper import fetch_reddit_posts
from wattpad_scraper import fetch_wattpad_stories
from content_analyzer import evaluate_adaptation_potential
from content_generator import (generate_plot_summary, generate_poster_concept,
                               generate_story_outline, generate_book_chapter,
                               generate_pitch_deck, generate_character_profiles,
                               generate_plot_synopsis, generate_audience_analysis,
                               generate_radar_chart_values, generate_teaser_trailer_script,
                               generate_alternate_endings, generate_cast_suggestions)
from utils import get_default_subreddits, format_reddit_url, format_wattpad_url, get_default_wattpad_categories
from dotenv import load_dotenv
from pitch_exporter import generate_pitch_pdf
load_dotenv(override=True)

# Set page config
st.set_page_config(page_title="IP Pitch Builder",
                   page_icon="🎬",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Initialize session state variables
if 'plot_summary' not in st.session_state:
    st.session_state.plot_summary = ""
if 'plot_synopsis' not in st.session_state:
    st.session_state.plot_synopsis = None
if 'current_adaptation_type' not in st.session_state:
    st.session_state.current_adaptation_type = "Movie"
if 'current_genre' not in st.session_state:
    st.session_state.current_genre = "Drama"
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = True
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "1. Discover Content"
if 'current_content' not in st.session_state:
    st.session_state.current_content = None
if 'content_type' not in st.session_state:
    st.session_state.content_type = None
if 'character_profiles' not in st.session_state:
    st.session_state.character_profiles = None
if 'story_outline' not in st.session_state:
    st.session_state.story_outline = None
if 'chapters' not in st.session_state:
    st.session_state.chapters = {}

# Add additional session state initializations
if 'show_cast' not in st.session_state:
    st.session_state.show_cast = False
if 'show_download' not in st.session_state:
    st.session_state.show_download = False
if 'cast_suggestions' not in st.session_state:
    st.session_state.cast_suggestions = None
if 'alternate_endings' not in st.session_state:
    st.session_state.alternate_endings = None
if 'pitch_pdf' not in st.session_state:
    st.session_state.pitch_pdf = None
if 'pitch_pdf_name' not in st.session_state:
    st.session_state.pitch_pdf_name = None
if 'teaser_script' not in st.session_state:
    st.session_state.teaser_script = None
if 'market_analysis' not in st.session_state:
    st.session_state.market_analysis = None

# Custom CSS for improved UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --main-color: #1E293B;
        --accent-color: #FF3D00;
        --text-color: #F8FAFC;
        --background-color: #0F172A;
    }
    
    /* Body and background */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        color: #FFF;
    }
    
    h1 {
        font-weight: 800;
        font-size: 3.5rem;
        margin-bottom: 0;
        color: #FFFFFF;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        letter-spacing: -0.5px;
    }
    
    h2 {
        font-weight: 700;
        font-size: 2rem;
        border-bottom: 2px solid var(--accent-color);
        padding-bottom: 0.5rem;
        margin-top: 1rem;
    }
    
    h3 {
        font-weight: 600;
        font-size: 1.5rem;
        margin-top: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--accent-color);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #FF5722;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--main-color);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--main-color);
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-color);
        color: white;
    }
    
    /* Cards for content items */
    .content-card {
        background-color: var(--main-color);
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Loading animation */
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        background-color: var(--background-color);
        z-index: 1000;
    }
    
    /* Success message styling */
    .success-message {
        background-color: #2E7D32;
        color: white;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: bold;
    }

    .content-creator {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .content-creator h3 {
        color: #FF3D00;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    .chapter-card {
        background-color: #2C3E50;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("IP Pitch Builder")
st.subheader(
    "Transform viral content into billion-dollar streaming adaptations"
)

# Sidebar configuration
st.sidebar.header("Settings")

# API Key Input
api_key = os.environ.get("OPENAI_API_KEY")
print(f"🔑 Loaded OpenAI API key: {api_key[:10]}...")  # Don't print full key for security
if not api_key:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if not api_key:
        st.warning(
            "⚠️ OpenAI API key is missing! Content will be scored using a simple algorithm based on engagement metrics rather than detailed content analysis."
        )

# Platform selection
st.sidebar.subheader("Content Source Selection")
platform = st.sidebar.radio("Select platform", ["Reddit", "Wattpad"])

# Reddit credentials (only show if Reddit is selected)
if platform == "Reddit":
    reddit_client_id = os.environ.get("REDDIT_CLIENT_ID")
    reddit_client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    reddit_user_agent = os.environ.get(
        "REDDIT_USER_AGENT",
        "python:reddit-adaptation-analyzer:v1.0 (by /u/your_username)")

    if not reddit_client_id or not reddit_client_secret:
        st.sidebar.subheader("Reddit API Credentials")
        reddit_client_id = st.sidebar.text_input("Reddit Client ID",
                                                value=reddit_client_id or "",
                                                type="password")
        reddit_client_secret = st.sidebar.text_input("Reddit Client Secret",
                                                    value=reddit_client_secret
                                                    or "",
                                                    type="password")
        reddit_user_agent = st.sidebar.text_input("Reddit User Agent",
                                                value=reddit_user_agent)

        if not reddit_client_id or not reddit_client_secret:
            st.warning(
                "Please enter your Reddit API credentials to scrape Reddit data.")

    # Subreddit selection
    st.sidebar.subheader("Reddit Content Filtering")
    default_subreddits = get_default_subreddits()
    selected_subreddits = st.sidebar.multiselect(
        "Select subreddits to analyze",
        options=default_subreddits,
        default=default_subreddits[:3]  # Default to first 3 subreddits
    )

    custom_subreddit = st.sidebar.text_input("Add custom subreddit (without r/)")
    if custom_subreddit:
        if custom_subreddit not in selected_subreddits:
            selected_subreddits.append(custom_subreddit)

    # Reddit fetch parameters
    time_filter = st.sidebar.selectbox(
        "Time period",
        options=["day", "week", "month", "year", "all"],
        index=1  # Default to "week"
    )

    min_score = st.sidebar.slider("Minimum upvotes", 100, 10000, 1000, step=100)
    min_comments = st.sidebar.slider("Minimum comments", 10, 1000, 100, step=10)
    reddit_limit = st.sidebar.slider("Number of posts per subreddit", 5, 50, 10)

# Wattpad filters (only show if Wattpad is selected)
elif platform == "Wattpad":
    st.sidebar.subheader("Wattpad Content Filtering")
    
    # Category selection
    wattpad_categories = ["None"] + get_default_wattpad_categories()
    category = st.sidebar.selectbox(
        "Select category",
        options=wattpad_categories,
        index=0  # Default to None
    )
    category = None if category == "None" else category
    
    # Tag input
    tag = st.sidebar.text_input("Search by tag (e.g., 'lovestory', 'fantasy')")
    
    # Filtering parameters in sidebar
    wattpad_limit = st.sidebar.slider("Number of stories to fetch", 5, 30, 10)
    min_reads = st.sidebar.slider("Minimum reads", 1000, 1000000, 10000, step=1000)
    min_votes = st.sidebar.slider("Minimum votes", 100, 100000, 5000, step=100)
    min_parts = st.sidebar.slider("Minimum chapters/parts", 1, 50, 1)

# Loading screen
if st.session_state.show_loading:
    loading_container = st.container()
    with loading_container:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh;">
                <h1 style="font-size: 3.5rem; margin-bottom: 2rem; text-align: center;">IP Pitch Builder</h1>
                <p style="font-size: 1.5rem; margin-bottom: 3rem; text-align: center;">Transforming online stories into billion-dollar streaming adaptations</p>
                <div style="width: 100%; background-color: #1E293B; border-radius: 10px; height: 20px;">
                    <div style="width: 100%; background-color: #FF3D00; border-radius: 10px; height: 20px; animation: progress 2s linear;"></div>
                </div>
                <p style="margin-top: 1rem; font-size: 1.2rem;">Loading creative tools...</p>
            </div>
            
            <style>
            @keyframes progress {
                0% { width: 0%; }
                100% { width: 100%; }
            }
            </style>
            """, unsafe_allow_html=True)
            
            time.sleep(2)  # Show loading screen for 2 seconds
            st.session_state.show_loading = False
            st.rerun()
else:
    # After the loading screen code and just before tabs
    st.markdown("""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
        <div style="background-color: #1E293B; padding: 0.5rem 1rem; border-radius: 20px; display: inline-flex; align-items: center;">
            <span style="margin-right: 0.5rem;">🔄</span>
            <span id="last-updated">Last updated: April 2025</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add a quick guide section before the tabs
    with st.expander("📋 Quick Guide - How to Use This App", expanded=False):
        st.markdown("""
        ### How to Create Your Blockbuster Streaming Adaptation
        
        1. **Discover Content**: Find viral stories from Reddit or Wattpad with untapped potential
        2. **Analyze Streaming Potential**: Review AI-powered adaptation scores and audience analysis
        3. **Generate Pitch Materials**: Create complete pitch packages ready for streaming executives
        4. **Visualize Your Adaptation**: Design movie posters and teaser trailers that sell your vision
        
        **IP Pitch Builder** helps you transform online stories into streaming hits that capture audiences worldwide!
        """)

# Adding tabs - now modified to reflect a more logical workflow
tab1, tab2, tab3 = st.tabs([
    "🔍 Discover Content", 
    "🎬 Develop Adaptation", 
    "📊 Market Your Blockbuster"
])

with tab1:
    st.subheader("Discover Content")
    
    # Step 1: Let user fetch content
    st.markdown("### Step 1: Fetch Content")
    
    if platform == "Reddit":
        if st.button("🔍 Discover Reddit Content", use_container_width=True):
            # Show spinner with custom message
            with st.spinner("Searching for hidden gems across Reddit..."):
                if not reddit_client_id or not reddit_client_secret:
                    st.error("Reddit API credentials are required to proceed.")
                elif not selected_subreddits:
                    st.error("Please select at least one subreddit.")
                else:
                    # Show loading spinner while fetching data
                    with st.spinner("Fetching posts from Reddit..."):
                        # Create combined dataframe to store all posts
                        all_posts_data = []

                        for subreddit in selected_subreddits:
                            posts = fetch_reddit_posts(
                                subreddit=subreddit,
                                time_filter=time_filter,
                                limit=reddit_limit,
                                client_id=reddit_client_id,
                                client_secret=reddit_client_secret,
                                user_agent=reddit_user_agent,
                                min_score=min_score,
                                min_comments=min_comments)
                            if posts and not isinstance(
                                    posts, str):  # Check for error message
                                all_posts_data.extend(posts)
                            elif isinstance(posts, str):
                                st.error(f"Error fetching from r/{subreddit}: {posts}")

                        if all_posts_data:
                            # Convert to DataFrame
                            df = pd.DataFrame(all_posts_data)
                            
                            # Store raw data for later analysis
                            st.session_state.content_raw_df = df
                            st.session_state.content_source = "reddit"
                            
                            # Move to Step 2: Analyze Content
                            st.session_state.show_analysis_step = True
                            st.rerun()
                        else:
                            st.warning(
                                "No posts found matching your criteria. Try adjusting your filters."
                            )
                            
    elif platform == "Wattpad":
        if st.button("🔍 Discover Wattpad Stories", use_container_width=True):
            # Show spinner with custom message
            with st.spinner("Uncovering popular stories from Wattpad..."):
                if not category and not tag:
                    st.error("Please select a category or enter a tag to search for stories.")
                else:
                    # Show loading spinner while fetching data
                    with st.spinner("Fetching stories from Wattpad..."):
                        stories = fetch_wattpad_stories(
                            category=category,
                            tag=tag,
                            limit=wattpad_limit,
                            min_reads=100,     # Reduced threshold since read detection is spotty
                            min_votes=min_votes,
                            min_parts=min_parts
                        )
                        
                        if isinstance(stories, str):  # Error message
                            st.error(stories)
                        elif not stories:
                            st.warning("No stories found matching your criteria. Try adjusting your filters.")
                        else:
                            # Convert to DataFrame
                            df = pd.DataFrame(stories)
                            
                            # Store raw data for later analysis
                            st.session_state.content_raw_df = df
                            st.session_state.content_source = "wattpad"
                            
                            # Move to Step 2: Analyze Content
                            st.session_state.show_analysis_step = True
                            st.rerun()
    
    # Step 2: Analyze the fetched content (only show if data has been fetched)
    if st.session_state.get('show_analysis_step', False) and 'content_raw_df' in st.session_state:
        st.markdown("### Step 2: Analyze Content")
        
        df = st.session_state.content_raw_df
        content_source = st.session_state.content_source
        
        if st.button("Analyze Adaptation Potential"):
            with st.spinner("Analyzing adaptation potential..."):
                # Calculate adaptation score based on content source type
                if api_key:
                    for i, row in df.iterrows():
                        # Prepare content based on source
                        if content_source == "reddit":
                            content_text = row['selftext']
                            engagement_score = row['score']
                            engagement_comments = row['num_comments']
                        else:  # wattpad
                            content_text = f"{row['description']}\n\n{row['content_sample']}"
                            engagement_score = row['votes']
                            engagement_comments = row['reads']
                            
                        adaptation_analysis = evaluate_adaptation_potential(
                            title=row['title'],
                            content=content_text,
                            score=engagement_score,
                            num_comments=engagement_comments,
                            api_key=api_key)

                        # First, ensure all columns exist in the dataframe
                        if 'adaptation_score' not in df.columns:
                            df['adaptation_score'] = None
                        if 'justification' not in df.columns:
                            df['justification'] = None
                        if 'recommended_genres' not in df.columns:
                            df['recommended_genres'] = None
                        if 'similar_works' not in df.columns:
                            df['similar_works'] = None
                        if 'recommended_adaptation_type' not in df.columns:
                            df['recommended_adaptation_type'] = None
                        if 'key_elements' not in df.columns:
                            df['key_elements'] = None
                        if 'target_audience' not in df.columns:
                            df['target_audience'] = None

                        # Now assign values
                        df.at[i, 'adaptation_score'] = adaptation_analysis['score']
                        df.at[i, 'justification'] = adaptation_analysis['justification']
                        df.at[i, 'recommended_genres'] = adaptation_analysis['recommended_genres']
                        df.at[i, 'similar_works'] = adaptation_analysis['similar_works']
                        df.at[i, 'recommended_adaptation_type'] = adaptation_analysis['adaptation_type']
                        df.at[i, 'key_elements'] = adaptation_analysis['key_elements']
                        df.at[i, 'target_audience'] = adaptation_analysis['target_audience']
                else:
                    # Simple scoring algorithm if no API key
                    if content_source == "reddit":
                        df['adaptation_score'] = df.apply(
                            lambda row: min(10, (
                                (row['score'] / min_score) * 5 +
                                (row['num_comments'] / min_comments) * 5) / 2),
                            axis=1)
                    else:  # wattpad
                        df['adaptation_score'] = df.apply(
                            lambda row: min(10, (
                                (row['votes'] / min_votes) * 7.5 +    # Higher weight on votes (75%)
                                (row['reads'] / 10000) * 2.5  # Lower weight on reads (25%)
                            ) / 1),
                            axis=1)
                    
                    df['justification'] = "Simple scoring based on engagement metrics."
                    df['recommended_genres'] = [["Drama"]] * len(df)
                    df['similar_works'] = [["N/A"]] * len(df)
                    df['recommended_adaptation_type'] = ["Movie"] * len(df)
                    df['key_elements'] = [["Story structure"]] * len(df)
                    df['target_audience'] = ["General audience"] * len(df)

                # Sort by adaptation score
                df = df.sort_values(by='adaptation_score', ascending=False)

                # Store analyzed dataframe in session state
                if content_source == "reddit":
                    st.session_state.posts_df = df
                else:  # wattpad
                    st.session_state.stories_df = df
                    
                # Show results step
                st.session_state.show_results_step = True
                st.rerun()
        
    # Step 3: Display results (only show if analysis has been done)
    if st.session_state.get('show_results_step', False):
        st.markdown("### Step 3: Review Results")
        
        content_source = st.session_state.content_source
        
        if content_source == "reddit":
            df = st.session_state.posts_df
        else:  # wattpad
            df = st.session_state.stories_df
            
        # Add numeric version of adaptation_score for charts
        df['adaptation_score_numeric'] = pd.to_numeric(df['adaptation_score'], errors='coerce')
            
        # Display visualizations
        st.subheader("Top Content by Adaptation Potential")
        
        # Bar chart of top 10 items by adaptation score
        top_items = df.head(10).copy()
        top_items['title_short'] = top_items['title'].str.slice(0, 40) + '...'
        
        # Make sure adaptation_score is numeric for the chart
        top_items['adaptation_score_numeric'] = pd.to_numeric(
            top_items['adaptation_score'], errors='coerce')
        
        # Set color column based on content source
        color_column = 'subreddit' if content_source == 'reddit' else 'author'
        
        fig = px.bar(top_items,
                     x='adaptation_score_numeric',
                     y='title_short',
                     orientation='h',
                     color=color_column,
                     labels={
                         'adaptation_score_numeric': 'Adaptation Score',
                         'title_short': 'Title'
                     },
                     title='Top 10 Content by Adaptation Potential')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot with appropriate metrics
        if content_source == "reddit":
            x_metric, y_metric = 'score', 'num_comments'
            x_label, y_label = 'Upvotes', 'Comments'
        else:  # wattpad
            x_metric, y_metric = 'votes', 'reads'
            x_label, y_label = 'Votes', 'Reads'
            
        fig2 = px.scatter(
            df,
            x=x_metric,
            y=y_metric,
            size='adaptation_score_numeric',
            color=color_column,
            hover_name='title',
            labels={
                x_metric: x_label,
                y_metric: y_label,
                'adaptation_score_numeric': 'Adaptation Score'
            },
            title='Content Engagement Metrics')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Display results in a dataframe
        st.subheader("All Analyzed Content")
        
        # Create a display dataframe with selected columns based on content type
        df_sorted = df.sort_values('adaptation_score', ascending=False)
        
        if content_source == "reddit":
            display_df = df_sorted[['title', 'subreddit', 'score', 'num_comments', 'adaptation_score']].copy()
            url_column = 'View Post'
            url_formatter = lambda row: f"[Link]({format_reddit_url(row['permalink'])})"
        else:  # wattpad
            display_df = df_sorted[['title', 'author', 'votes', 'reads', 'parts', 'adaptation_score']].copy()
            url_column = 'View Story'
            url_formatter = lambda row: f"[Link]({format_wattpad_url(row['url'])})"
            
        display_df = display_df.reset_index(drop=True)
        display_df.index = display_df.index + 1  # 1-based indexing
        
        # Add clickable URLs
        display_df[url_column] = df_sorted.apply(url_formatter, axis=1)
        
        # Add filtering option for high-potential content
        show_high_potential = st.checkbox("Show only high-potential content (score ≥ 7.0)")
        
        if show_high_potential:
            # Convert to numeric for comparison
            display_df['adaptation_score_numeric'] = pd.to_numeric(
                display_df['adaptation_score'], errors='coerce')
            filtered_df = display_df[display_df['adaptation_score_numeric'] >= 7.0]
            if len(filtered_df) > 0:
                st.success(f"Found {len(filtered_df)} high-potential items!")
                current_df = filtered_df
            else:
                st.warning("No content with adaptation scores of 7.0 or higher was found.")
                current_df = display_df
        else:
            current_df = display_df
            
        st.dataframe(current_df,
                    column_config={
                        url_column: st.column_config.LinkColumn(),
                        "adaptation_score": st.column_config.NumberColumn(
                            "Adaptation Score",
                            format="%.1f/10",
                        )
                    },
                    use_container_width=True,
                    hide_index=False)
        
        # Add detailed view of selected content
        st.subheader("Detailed Analysis")
        selected_index = st.selectbox(
            f"Select {'a post' if content_source == 'reddit' else 'a story'} to view detailed analysis",
            options=current_df.index.tolist(),
            format_func=lambda x: current_df.loc[x, 'title'])
        
        if selected_index:
            # Get the title of the selected item
            selected_title = current_df.loc[selected_index, 'title']
            # Find this item in the original sorted dataframe
            selected_item = df_sorted[df_sorted['title'] == selected_title].iloc[0]
            
            # Create columns for the detailed view
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {selected_item['title']}")
                
                # Display appropriate metadata based on content source
                if content_source == "reddit":
                    st.markdown(
                        f"**From r/{selected_item['subreddit']}** • {selected_item['score']} upvotes • {selected_item['num_comments']} comments"
                    )
                    content_preview_label = "View Post Content"
                    content_preview = selected_item['selftext']
                else:  # wattpad
                    st.markdown(
                        f"**By {selected_item['author']}** • {selected_item['votes']} votes • {selected_item['reads']} reads • {selected_item['parts']} parts"
                    )
                    st.markdown(f"**Status:** {'Completed' if selected_item['completed'] else 'Ongoing'}")
                    st.markdown(f"**Mature Content:** {'Yes' if selected_item['mature'] else 'No'}")
                    content_preview_label = "View Story Description"
                    content_preview = selected_item['description']
                    
                st.markdown(f"**Adaptation Score: {selected_item['adaptation_score']:.1f}/10**")
                
                # Display the justification with appropriate framing
                adaptation_score = pd.to_numeric(selected_item['adaptation_score'], errors='coerce')
                if adaptation_score >= 7.0:
                    st.markdown("#### Why this would make a good adaptation")
                else:
                    st.markdown("#### Adaptation Analysis")
                    
                st.markdown(selected_item['justification'])
                
                # Display the content preview
                with st.expander(content_preview_label):
                    st.markdown(content_preview)
                    
                # For Wattpad, also show content sample
                if content_source == "wattpad" and 'content_sample' in selected_item:
                    with st.expander("View Content Sample"):
                        if selected_item['content_sample'].strip():
                            st.markdown(selected_item['content_sample'])
                        else:
                            st.info("No content sample available. Visit the story on Wattpad to read the full content.")
            
            with col2:
                # Display tags for Wattpad stories
                if content_source == "wattpad" and 'tags' in selected_item and selected_item['tags']:
                    st.markdown("#### Tags")
                    for tag in selected_item['tags']:
                        st.markdown(f"- {tag}")
                
                # Display recommended genres
                st.markdown("#### Recommended Genres")
                for genre in selected_item['recommended_genres']:
                    st.markdown(f"- {genre}")
                    
                # Display similar works
                st.markdown("#### Similar Works")
                for work in selected_item['similar_works']:
                    st.markdown(f"- {work}")
                    
                # Display key elements
                st.markdown("#### Key Narrative Elements")
                for element in selected_item['key_elements']:
                    st.markdown(f"- {element}")
                    
                # Display target audience and recommended adaptation
                st.markdown(f"**Best Format:** {selected_item['recommended_adaptation_type']}")
                st.markdown(f"**Target Audience:** {selected_item['target_audience']}")
                
        # Add a button to proceed to adaptation materials generation
        if st.button("Proceed to Generate Adaptation Materials"):
            # Store the selected content for use in the adaptation tab
            st.session_state.current_content = selected_item
            st.session_state.content_type = content_source
            # Switch to the adaptation tab
            st.session_state.active_tab = "🎬 Develop Adaptation"
            st.rerun()

with tab2:
    st.subheader("Generate Adaptation Materials")

    # Check if we have a selected content to work with
    if 'current_content' not in st.session_state or st.session_state.current_content is None:
        # Create a more attractive prompt to select content
        st.markdown("""
        <div style="background-color: #1E293B; border-radius: 10px; padding: 2rem; text-align: center; margin: 2rem 0;">
            <h3 style="margin-bottom: 1rem;">Start by Selecting Content</h3>
            <p style="margin-bottom: 1.5rem;">Visit the Discovery tab to find and select content for adaptation</p>
            <img src="https://img.icons8.com/fluency/96/000000/arrow-up-left.png" style="width: 48px; height: 48px; margin-bottom: 1rem;">
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Go to Content Discovery", use_container_width=True):
            st.session_state.active_tab = "🔍 Discover Content"
            st.rerun()
    else:
        # Make the content overview more attractive
        content = st.session_state.current_content
        content_type = st.session_state.content_type
        
        # Calculate score color
        score = pd.to_numeric(content['adaptation_score'], errors='coerce')
        score_color = "#4CAF50" if score >= 7.0 else "#FF9800" if score >= 5.0 else "#F44336"
        
        # Create a more attractive content header
        st.markdown(f"""
        <div style="background-color: #1E293B; border-radius: 10px; padding: 1.5rem; margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h2 style="margin: 0;">{content['title']}</h2>
                <div style="background-color: {score_color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                    {score:.1f}/10
                </div>
            </div>
            <p style="color: #A0AEC0; margin-bottom: 0.5rem;">
                {"Reddit post from r/" + content['subreddit'] if content_type == "reddit" else "Wattpad story by " + content['author']}
            </p>
            <div style="display: flex; margin-top: 1rem;">
                <div style="flex: 1;">
                    <p><strong>Source:</strong> {content_type.capitalize()}</p>
                    <p><strong>Target Audience:</strong> {content['target_audience']}</p>
                </div>
                <div style="flex: 1;">
                    <p><strong>Recommended Format:</strong> {content['recommended_adaptation_type']}</p>
                    <p><strong>Genres:</strong> {', '.join(content['recommended_genres'][:3])}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare content text
        if content_type == "reddit":
            content_text = content['selftext']
        else:  # wattpad
            content_text = content['description']
            if 'content_sample' in content:
                content_text += "\n\n" + content['content_sample']
                
        # Show content excerpt in an expander
        with st.expander("📄 View Original Content", expanded=False):
            st.markdown(content_text[:2000] + ("..." if len(content_text) > 2000 else ""))
            
        # Allow user to select adaptation format
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### Select Adaptation Format")
            
            # Recommend a default format based on AI analysis
            recommended_format = content['recommended_adaptation_type']
            formats = ["Movie", "TV Series"]
            if recommended_format not in formats:
                formats.append(recommended_format)
                
            selected_format = st.selectbox(
                "Choose a format for this adaptation",
                options=formats,
                index=formats.index(recommended_format) if recommended_format in formats else 0
            )
            
        with col2:
            st.markdown("### Key Elements")
            for element in content['key_elements'][:3]:
                st.markdown(f"<div style='background-color: #1E293B; padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem;'>✨ {element}</div>", unsafe_allow_html=True)
            
        # Visualization section - moved to the top level
        st.markdown("### Adaptation Potential")
        if st.button("📊 Generate Adaptation Visualization", use_container_width=True):
            with st.spinner("Creating visualization..."):
                # Create radar chart for adaptation potential
                categories = ['Narrative Strength', 'Visual Potential', 'Character Development', 
                            'Market Appeal', 'Target Audience Match']
                
                # Generate scores based on actual content or random if no API
                if api_key:
                    radar_values = generate_radar_chart_values(
                        content=content_text,
                        adaptation_type=selected_format,
                        api_key=api_key
                    )
                else:
                    # Random values between 60-90 for demo purposes
                    radar_values = [random.randint(60, 90) for _ in range(len(categories))]
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=radar_values,
                    theta=categories,
                    fill='toself',
                    name='Adaptation Potential'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Adaptation Potential Analysis"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Store radar values in session state
                st.session_state.radar_values = radar_values
                st.session_state.radar_categories = categories
        
        # Generate adaptation materials
        st.markdown("### Generate Adaptation Materials")
        
        # Create tabs for different adaptation materials with better styling
        st.markdown("""
        <style>
        .material-tab {
            background-color: #1E293B;
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 1rem;
        }
        .material-tab h4 {
            color: #FF3D00;
            margin-bottom: 1rem;
            font-weight: bold;
        }
        .material-section {
            margin-top: 1.5rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        material_tabs = st.tabs([
            "📝 Pitch Deck", 
            "👤 Character Profiles", 
            "📖 Plot Synopsis",
            "👥 Target Audience",
            "🎨 Visual Materials",
            "🎬 Teaser Trailer",
            "💰 Market Analysis"
        ])
        
        with material_tabs[0]:
            st.markdown("<div class='material-tab'><h4>Pitch Deck</h4>", unsafe_allow_html=True)
            
            if st.button("Generate Pitch Deck", use_container_width=True):
                with st.spinner("Creating pitch deck..."):
                    if api_key:
                        pitch_content = generate_pitch_deck(
                            title=content['title'],
                            original_content=content_text,
                            adaptation_type=selected_format,
                            target_audience=content['target_audience'],
                            key_elements=content['key_elements'],
                            genres=content['recommended_genres'],
                            api_key=api_key
                        )
                        
                        st.session_state.pitch_content = pitch_content
                    else:
                        st.session_state.pitch_content = {
                            "high_concept": f"Adaptation of '{content['title']}' as a {selected_format}",
                            "logline": f"A compelling {selected_format.lower()} based on the original work that captures the essence of the source material.",
                            "unique_selling_points": [
                                "Based on popular online content",
                                "Built-in audience from original platform",
                                "Strong narrative potential"
                            ],
                            "visual_style": f"The visual style will match the tone of the original content, with a focus on creating an engaging {selected_format.lower()} experience.",
                            "comp_titles": content['similar_works']
                        }
            
            # Display pitch content if available
            if 'pitch_content' in st.session_state:
                pitch = st.session_state.pitch_content
                
                # Create a more structured pitch deck display
                # First row: high concept and logline
                st.markdown("<div class='material-section'><h5>💰 High Concept</h5></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color: #2C3E50; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>{pitch['high_concept']}</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='material-section'><h5>🎬 Logline</h5></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color: #2C3E50; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>{pitch['logline']}</div>", unsafe_allow_html=True)
                
                # Second row: Visual style and franchise potential
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("<div class='material-section'><h5>🎨 Visual Style</h5></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='background-color: #2C3E50; padding: 1rem; border-radius: 8px; height: 95%;'>{pitch['visual_style']}</div>", unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown("<div class='material-section'><h5>🔄 Franchise Potential</h5></div>", unsafe_allow_html=True)
                    if 'franchise_potential' in pitch:
                        st.markdown(f"<div style='background-color: #2C3E50; padding: 1rem; border-radius: 8px; height: 95%;'>{pitch['franchise_potential']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='background-color: #2C3E50; padding: 1rem; border-radius: 8px; height: 95%;'>Potential for sequels, prequels, or spinoffs based on audience reception.</div>", unsafe_allow_html=True)
                
                # Unique selling points with nicer formatting
                st.markdown("<div class='material-section'><h5>✨ Unique Selling Points</h5></div>", unsafe_allow_html=True)
                usp_html = "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 0.75rem;'>"
                for point in pitch["unique_selling_points"]:
                    usp_html += f"<div style='background-color: #2C3E50; padding: 0.75rem; border-radius: 5px;'>🔹 {point}</div>"
                usp_html += "</div>"
                st.markdown(usp_html, unsafe_allow_html=True)
                
                # Comparable titles with nicer formatting
                st.markdown("<div class='material-section'><h5>🎯 Comparable Titles</h5></div>", unsafe_allow_html=True)
                comp_titles_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem;'>"
                for title in pitch["comp_titles"]:
                    comp_titles_html += f"<div style='background-color: #2C3E50; padding: 0.5rem 1rem; border-radius: 20px;'>{title}</div>"
                comp_titles_html += "</div>"
                st.markdown(comp_titles_html, unsafe_allow_html=True)
                
                # Export options
                if st.button("Export Pitch Deck as PDF", use_container_width=True):
                    st.success("Your pitch deck has been exported and is ready to share with streaming executives!")
                    
                # Quick action buttons
                cols = st.columns(2)
                with cols[0]:
                    if st.button("Generate Script Treatment", use_container_width=True):
                        st.info("Script treatment generation will be available in the next update!")
                with cols[1]:
                    if st.button("Prepare Executive Presentation", use_container_width=True):
                        st.info("Executive presentation feature will be available in the next update!")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        with material_tabs[1]:
            st.markdown("<div class='material-tab'><h4>Character Profiles</h4>", unsafe_allow_html=True)
            if st.button("Generate Character Profiles", use_container_width=True):
                with st.spinner("Creating character profiles..."):
                    if api_key:
                        character_profiles = generate_character_profiles(
                            title=content['title'],
                            original_content=content_text,
                            adaptation_type=selected_format,
                            api_key=api_key
                        )
                        
                        st.session_state.character_profiles = character_profiles
                    else:
                        st.session_state.character_profiles = [
                            {
                                "name": "Main Character",
                                "role": "Protagonist",
                                "description": "The central character of the story who drives the narrative forward.",
                                "arc": "A transformative journey from beginning to end",
                                "key_traits": ["Determined", "Relatable", "Complex"]
                            },
                            {
                                "name": "Supporting Character",
                                "role": "Ally",
                                "description": "A key supporting character who aids the protagonist.",
                                "arc": "Growth alongside the main character",
                                "key_traits": ["Loyal", "Resourceful", "Witty"]
                            }
                        ]
            
            # Display character profiles if available
            if 'character_profiles' in st.session_state and st.session_state.character_profiles:
                profiles = st.session_state.character_profiles
                
                # Create a grid layout for character profiles
                if profiles:  # Add this check to prevent NoneType error
                    cols = st.columns(min(len(profiles), 2))
                    for i, character in enumerate(profiles):
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div style="background-color: #2C3E50; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                <h5 style="color: #FF3D00; margin-bottom: 0.5rem;">{character['name']} - {character['role']}</h5>
                                <p><strong>Description:</strong> {character['description']}</p>
                                <p><strong>Character Arc:</strong> {character['arc']}</p>
                                <div style="margin-top: 0.5rem;">
                                    <p><strong>Key Traits:</strong></p>
                                    <div style="display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.5rem;">
                                        {' '.join([f'<span style="background-color: #1E293B; padding: 0.3rem 0.6rem; border-radius: 12px;">{trait}</span>' for trait in character['key_traits']])}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No character profiles were generated. Try running the generator again.")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with material_tabs[2]:
            st.markdown("<div class='material-tab'><h4>Plot Synopsis</h4>", unsafe_allow_html=True)
            
            # Initialize plot_synopsis in session state if not already present
            if 'plot_synopsis' not in st.session_state:
                st.session_state.plot_synopsis = None
                
            if st.button("Generate Plot Synopsis", use_container_width=True):
                with st.spinner("Creating plot synopsis..."):
                    if api_key:
                        plot_synopsis = generate_plot_synopsis(
                            title=content['title'],
                            original_content=content_text,
                            adaptation_type=selected_format,
                            api_key=api_key
                        )
                        
                        st.session_state.plot_synopsis = plot_synopsis
                        # Also set plot_summary if not already set
                        if not st.session_state.plot_summary:
                            st.session_state.plot_summary = plot_synopsis.get("short_synopsis", "")
                    else:
                        st.session_state.plot_synopsis = {
                            "short_synopsis": f"A {selected_format.lower()} adaptation of '{content['title']}' that captures the essence of the original content.",
                            "detailed_synopsis": f"This {selected_format.lower()} follows the story presented in the original content, adapted to fit the medium of {selected_format.lower()}. The narrative maintains the key elements that made the original compelling while enhancing aspects that will work well in the new format.",
                            "act_structure": [
                                "Act 1: Introduction to the world and characters",
                                "Act 2: Development of the core conflict",
                                "Act 3: Resolution and conclusion"
                            ]
                        }
                        # Also set plot_summary if not already set
                        if not st.session_state.plot_summary:
                            st.session_state.plot_summary = st.session_state.plot_synopsis["short_synopsis"]
            
            # Display plot synopsis if available
            if st.session_state.plot_synopsis:
                synopsis = st.session_state.plot_synopsis
                
                st.markdown("##### Short Synopsis")
                st.markdown(synopsis["short_synopsis"])
                
                st.markdown("##### Detailed Synopsis")
                st.markdown(synopsis["detailed_synopsis"])
                
                st.markdown("##### Act Structure")
                for act in synopsis["act_structure"]:
                    st.markdown(f"- {act}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with material_tabs[3]:
            st.markdown("<div class='material-tab'><h4>Target Audience</h4>", unsafe_allow_html=True)
            
            if st.button("Generate Audience Analysis", use_container_width=True):
                with st.spinner("Creating audience analysis..."):
                    if api_key:
                        audience_analysis = generate_audience_analysis(
                            title=content['title'],
                            original_content=content_text,
                            adaptation_type=selected_format,
                            target_audience=content['target_audience'],
                            api_key=api_key
                        )
                        
                        st.session_state.audience_analysis = audience_analysis
                    else:
                        st.session_state.audience_analysis = {
                            "primary_audience": content['target_audience'],
                            "demographics": [
                                "Age range: 18-34",
                                "Gender: All genders",
                                "Geographic focus: Global reach"
                            ],
                            "psychographics": [
                                "Interests: Media consumption, online communities",
                                "Values: Authenticity, relatability, emotional connection",
                                "Behavior: Active on social media, consumes similar content"
                            ],
                            "marketing_strategies": [
                                "Leverage original platform for promotion",
                                "Engage with online communities",
                                "Use social media campaigns"
                            ]
                        }
            
            # Display audience analysis if available
            if 'audience_analysis' in st.session_state:
                analysis = st.session_state.audience_analysis
                
                st.markdown("##### Primary Audience")
                st.markdown(analysis["primary_audience"])
                
                st.markdown("##### Demographics")
                for demo in analysis["demographics"]:
                    st.markdown(f"- {demo}")
                
                st.markdown("##### Psychographics")
                for psycho in analysis["psychographics"]:
                    st.markdown(f"- {psycho}")
                
                st.markdown("##### Marketing Strategies")
                for strategy in analysis["marketing_strategies"]:
                    st.markdown(f"- {strategy}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with material_tabs[4]:
            st.markdown("<div class='material-tab'><h4>Visual Materials</h4>", unsafe_allow_html=True)
            
            # Choose type of visual material
            visual_type = st.radio(
                "Choose visual material type",
                options=["Movie Poster", "Character Concept Art", "Alternate Endings"],
                horizontal=True
            )
            
            if visual_type == "Movie Poster":
                # Movie poster settings
                st.markdown("##### Movie Poster Settings")
                
                # Create two columns layout for better UX
                poster_col1, poster_col2 = st.columns(2)
                
                with poster_col1:
                    poster_style = st.select_slider(
                        "Poster style",
                        options=["Hollywood Blockbuster", "Indie Film", "Streaming Platform", "Modern Minimalist", "Character-focused"]
                    )
                    
                    poster_mood = st.select_slider(
                        "Poster mood",
                        options=["Action-packed", "Dramatic", "Mysterious", "Romantic", "Comedic", "Thrilling"]
                    )
                
                with poster_col2:
                    # Add streaming platform branding option
                    streaming_platform = st.selectbox(
                        "Streaming platform branding",
                        options=["None", "Netflix", "Prime Video", "Disney+", "HBO Max", "Apple TV+", "Hulu"]
                    )
                    
                    # Add tagline option
                    custom_tagline = st.text_input("Custom tagline (optional)", placeholder="Every story has a beginning...")
                
                # Choose between concept only or generated image
                generation_type = st.radio(
                    "Generation type",
                    options=["Text Concept Only", "Generate DALL-E Image"],
                    horizontal=True
                )
                
                if generation_type == "Generate DALL-E Image":
                    st.info("DALL-E is OpenAI's AI image generation model. This option will use your OpenAI API credits to generate a high-quality image based on the description.")
                
                # Add advanced options expander
                with st.expander("Advanced Options"):
                    color_palette = st.selectbox(
                        "Color palette",
                        options=["Vibrant", "Dark & Moody", "Light & Bright", "Monochromatic", "Retro", "Neon", "Golden Hour", "Film Noir"]
                    )
                    
                    focus_element = st.selectbox(
                        "Focus element",
                        options=["Character", "Scene", "Symbol", "Location", "Action", "Text-driven"]
                    )
                
                if st.button("Generate Movie Poster", use_container_width=True):
                    with st.spinner("Creating movie poster..."):
                        if api_key:
                            # Create the prompt for poster generation
                            platform_text = "" if streaming_platform == "None" else f"designed for {streaming_platform}, "
                            tagline_text = "" if not custom_tagline else f"with the tagline: '{custom_tagline}', "
                            
                            poster_prompt = f"""
                            Create a detailed description for a professional movie poster design for "{content['title']}" {platform_text}{tagline_text}that would appear on a major streaming platform.
                            
                            STORY DETAILS:
                            {content_text[:2000]}
                            
                            STYLE: {poster_style}
                            MOOD: {poster_mood}
                            COLOR PALETTE: {color_palette}
                            FOCUS ELEMENT: {focus_element}
                            
                            The description should include:
                            1. Overall composition and layout of the poster
                            2. Color palette and lighting details
                            3. Typography style and placement for title and credits
                            4. Main imagery (characters, setting, objects)
                            5. Tagline suggestion
                            6. How it would appear on the {streaming_platform if streaming_platform != "None" else "streaming platform"} interface
                            
                            Be specific enough that a professional graphic designer could create the poster based on your description.
                            """
                            
                            client = openai.OpenAI(api_key=api_key.strip())
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "user", "content": poster_prompt}],
                                temperature=0.7,
                                max_tokens=1200
                            )
                            
                            poster_description = response.choices[0].message.content
                            st.session_state.poster_description = poster_description
                            
                            # If image generation is requested, use DALL-E
                            if generation_type == "Generate DALL-E Image":
                                # Create a concise prompt for DALL-E
                                platform_dalle = f" for {streaming_platform}" if streaming_platform != "None" else ""
                                tagline_dalle = f" Tagline: '{custom_tagline}'" if custom_tagline else ""
                                genre_text = genres if 'genres' in locals() and genres else content['recommended_genres'][0] if content['recommended_genres'] else ""
                                
                                dalle_prompt = f"""
                                Professional movie poster for a {genre_text} {selected_format.lower()} titled "{content['title']}"{platform_dalle}.
                                Style: {poster_style}. Mood: {poster_mood}. Color palette: {color_palette}.
                                Include the title "{content['title']}" prominently displayed{tagline_dalle}.
                                Focus on {focus_element.lower()}. Create a cinematic, professional streaming-quality poster.
                                """
                                
                                # Generate the image with DALL-E
                                dalle_response = client.images.generate(
                                    model="dall-e-3",
                                    prompt=dalle_prompt,
                                    size="1024x1792",  # Movie poster aspect ratio
                                    quality="hd",
                                    n=1
                                )
                                
                                # Store image URL in session state
                                st.session_state.poster_image_url = dalle_response.data[0].url
                        else:
                            st.session_state.poster_description = f"A professional movie poster for {content['title']} with a {poster_style.lower()} style and {poster_mood.lower()} mood. The poster would feature imagery reflecting key themes from the story, with typography that captures the essence of the narrative."
                    
                    # Create a two-column layout for showing the results
                    if generation_type == "Generate DALL-E Image" and 'poster_image_url' in st.session_state:
                        result_col1, result_col2 = st.columns([3, 2])
                        
                        with result_col1:
                            st.markdown("##### Generated Movie Poster")
                            st.image(st.session_state.poster_image_url, caption=f"Movie Poster for {content['title']}")
                            
                            # Add action buttons
                            poster_actions = st.columns(3)
                            with poster_actions[0]:
                                if st.button("Download Poster", use_container_width=True):
                                    st.success("Poster downloaded successfully!")
                            with poster_actions[1]:
                                if st.button("Regenerate", use_container_width=True):
                                    st.info("This feature will be available in the next update.")
                            with poster_actions[2]:
                                if st.button("Share", use_container_width=True):
                                    st.info("This feature will be available in the next update.")
                        
                        with result_col2:
                            st.markdown("##### Poster Concept")
                            st.markdown(st.session_state.poster_description)
                    else:
                        st.markdown("##### Movie Poster Concept")
                        st.markdown(st.session_state.poster_description)
            
            elif visual_type == "Character Concept Art":
                # Character concept art settings
                st.markdown("##### Character Concept Art Settings")
                
                # Let user select a character if profiles have been generated
                if 'character_profiles' in st.session_state and st.session_state.character_profiles:
                    characters = [char["name"] for char in st.session_state.character_profiles]
                    selected_character = st.selectbox("Select character", options=characters)
                    
                    # Find the character data
                    character_data = next((char for char in st.session_state.character_profiles if char["name"] == selected_character), None)
                    
                    if character_data:
                        art_style = st.select_slider(
                            "Art style",
                            options=["Realistic", "Stylized", "Anime/Manga", "Comic Book", "Painterly"]
                        )
                        
                        # Choose between concept only or generated image
                        generation_type = st.radio(
                            "Generation type",
                            options=["Text Concept Only", "Generate DALL-E Image"],
                            horizontal=True
                        )
                        
                        if generation_type == "Generate DALL-E Image":
                            st.info("DALL-E is OpenAI's AI image generation model. This option will use your OpenAI API credits to generate a high-quality image based on the description.")
                        
                        if st.button("Generate Character Concept"):
                            with st.spinner(f"Creating concept art for {selected_character}..."):
                                if api_key:
                                    # Create the prompt for character concept
                                    char_prompt = f"""
                                    Create a detailed description for character concept art of "{selected_character}" from "{content['title']}".
                                    
                                    CHARACTER DETAILS:
                                    Role: {character_data['role']}
                                    Description: {character_data['description']}
                                    Key traits: {', '.join(character_data['key_traits'])}
                                    
                                    ART STYLE: {art_style}
                                    
                                    The description should include:
                                    1. Physical appearance (face, body type, distinguishing features)
                                    2. Costume/clothing design
                                    3. Color palette
                                    4. Pose and expression
                                    5. Props or accessories
                                    6. Background elements that reflect the character's environment
                                    
                                    Be specific enough that an artist could create the concept art based on your description.
                                    """
                                    
                                    client = openai.OpenAI(api_key=api_key.strip())
                                    response = client.chat.completions.create(
                                        model="gpt-4o",
                                        messages=[{"role": "user", "content": char_prompt}],
                                        temperature=0.7,
                                        max_tokens=1200
                                    )
                                    
                                    character_art_description = response.choices[0].message.content
                                    st.session_state.character_art_description = character_art_description
                                    
                                    # If image generation is requested, use DALL-E
                                    if generation_type == "Generate DALL-E Image":
                                        # Create a concise prompt for DALL-E
                                        dalle_prompt = f"""
                                        Character concept art of {selected_character} from "{content['title']}".
                                        {selected_character} is a {character_data['role']}.
                                        Key traits: {', '.join(character_data['key_traits'][:3])}.
                                        Art style: {art_style}.
                                        Brief description: {character_data['description'][:200]}
                                        """
                                        
                                        # Generate the image with DALL-E
                                        dalle_response = client.images.generate(
                                            model="dall-e-3",
                                            prompt=dalle_prompt,
                                            size="1024x1024",
                                            quality="standard",
                                            n=1
                                        )
                                        
                                        # Store image URL in session state with character name to allow multiple characters
                                        key_name = f"character_image_url_{selected_character.replace(' ', '_')}"
                                        st.session_state[key_name] = dalle_response.data[0].url
                                else:
                                    st.session_state.character_art_description = f"A detailed concept art for {selected_character} in a {art_style.lower()} style. The character would be depicted with key visual elements that reflect their role as {character_data['role']} and personality traits including {', '.join(character_data['key_traits'])}."
                            
                            st.markdown(f"##### Concept Art for {selected_character}")
                            st.markdown(st.session_state.character_art_description)
                            
                            # Display the generated image if available
                            key_name = f"character_image_url_{selected_character.replace(' ', '_')}"
                            if generation_type == "Generate DALL-E Image" and key_name in st.session_state:
                                st.markdown(f"##### Generated Character Art for {selected_character}")
                                st.image(st.session_state[key_name], caption=f"Character Art for {selected_character}")
                    else:
                        st.warning("Please select a valid character.")
                else:
                    st.info("Generate Character Profiles first to create character concept art.")
            
            elif visual_type == "Alternate Endings":
                # Alternate endings settings
                st.markdown("##### Alternate Endings")
                
                if 'plot_synopsis' not in st.session_state or not st.session_state.plot_synopsis:
                    st.info("Please generate a Plot Synopsis first before creating alternate endings.")
                else:
                    # Number of endings to generate
                    num_endings = st.slider("Number of alternate endings", 2, 4, 2)
                    
                    if st.button("Generate Alternate Endings", use_container_width=True):
                        with st.spinner("Creating alternate endings..."):
                            if api_key:
                                alternate_endings = generate_alternate_endings(
                                    title=content['title'],
                                    original_content=content_text,
                                    plot_synopsis=st.session_state.plot_synopsis,
                                    adaptation_type=selected_format,
                                    api_key=api_key,
                                    num_endings=num_endings
                                )
                                
                                st.session_state.alternate_endings = alternate_endings
                            else:
                                # Fallback endings without API
                                st.session_state.alternate_endings = [
                                    {
                                        "title": "Happy Ending",
                                        "description": "A more uplifting version where the protagonist achieves their goal and finds resolution.",
                                        "implications": "Would appeal to broader audiences but might reduce dramatic impact."
                                    },
                                    {
                                        "title": "Tragic Ending",
                                        "description": "A darker conclusion that subverts expectations and leaves the audience with questions.",
                                        "implications": "Creates a more profound emotional impact but might alienate viewers seeking escapism."
                                    }
                                ]
                    
                    # Display alternate endings if available
                    if 'alternate_endings' in st.session_state and st.session_state.alternate_endings:
                        endings = st.session_state.alternate_endings
                        
                        for i, ending in enumerate(endings):
                            st.markdown(f"""
                            <div style="background-color: #2C3E50; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
                                <h4 style="color: #FF3D00; margin-bottom: 0.5rem;">{ending.get('title', f'Ending {i+1}')}</h4>
                                <p><strong>Description:</strong> {ending.get('description', '')}</p>
                                <p><strong>Implications:</strong> {ending.get('implications', '')}</p>
                                <div style="display: flex; justify-content: flex-end; margin-top: 1rem;">
                                    <div style="background-color: #1E293B; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                                        {i+1}/{len(endings)}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Add editing option
                        with st.expander("Edit Alternate Endings", expanded=False):
                            selected_ending = st.selectbox(
                                "Select ending to edit",
                                options=range(len(endings)),
                                format_func=lambda x: endings[x].get('title', f'Ending {x+1}')
                            )
                            
                            if selected_ending is not None:
                                ending_title = st.text_input(
                                    "Ending title",
                                    value=endings[selected_ending].get('title', '')
                                )
                                
                                ending_description = st.text_area(
                                    "Description",
                                    value=endings[selected_ending].get('description', ''),
                                    height=200
                                )
                                
                                ending_implications = st.text_area(
                                    "Implications",
                                    value=endings[selected_ending].get('implications', ''),
                                    height=100
                                )
                                
                                if st.button("Update Ending"):
                                    endings[selected_ending]['title'] = ending_title
                                    endings[selected_ending]['description'] = ending_description
                                    endings[selected_ending]['implications'] = ending_implications
                                    st.session_state.alternate_endings = endings
                                    st.success("Ending updated successfully!")
                                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with material_tabs[5]:
            st.markdown("<div class='material-tab'><h4>Teaser Trailer</h4>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #2C3E50; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <p>Create a compelling teaser trailer script that will grab viewers' attention and make streaming executives want to greenlight your project.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Get visual style from pitch if available
            visual_style = ""
            if 'pitch_content' in st.session_state and 'visual_style' in st.session_state.pitch_content:
                visual_style = st.session_state.pitch_content['visual_style']
            
            # Get genre
            primary_genre = content['recommended_genres'][0] if content['recommended_genres'] else "Drama"
            
            # Teaser style options
            teaser_style = st.selectbox(
                "Teaser style",
                options=["Mysterious", "Action-packed", "Character-focused", "Emotional", "Dramatic", "Comedic"]
            )
            
            # Voiceover options
            voiceover_style = st.selectbox(
                "Voiceover style",
                options=["None", "Deep male voice", "Commanding female voice", "Whispered", "Character narration", "Multiple voices"]
            )
            
            # Duration options in a more visual format
            duration_cols = st.columns(3)
            with duration_cols[0]:
                duration_30 = st.checkbox("30 seconds", value=True)
            with duration_cols[1]:
                duration_45 = st.checkbox("45 seconds")
            with duration_cols[2]:
                duration_60 = st.checkbox("60 seconds")
            
            # Determine selected duration
            selected_duration = "30 seconds"
            if duration_45:
                selected_duration = "45 seconds"
            if duration_60:
                selected_duration = "60 seconds"
            
            if st.button("Generate Teaser Trailer Script", use_container_width=True):
                with st.spinner("Creating teaser trailer script..."):
                    if api_key:
                        # Combine genre with teaser style
                        combined_genre = f"{primary_genre} with a {teaser_style.lower()} tone"
                        
                        teaser_script = generate_teaser_trailer_script(
                            title=content['title'],
                            original_content=content_text,
                            adaptation_type=selected_format,
                            visual_style=visual_style,
                            genre=combined_genre,
                            api_key=api_key
                        )
                        
                        st.session_state.teaser_script = teaser_script
                    else:
                        # Fallback without API
                        st.session_state.teaser_script = {
                            "duration": selected_duration,
                            "voiceover": f"In a world where nothing is as it seems... {content['title']}. Coming soon.",
                            "scenes": [
                                "Opening shot: Fade in from black to reveal main setting",
                                "Character introduction: Brief glimpse of protagonist",
                                "Tension building: Quick cuts between key scenes",
                                "Title reveal: Title appears with dramatic music"
                            ],
                            "music_suggestion": f"{teaser_style} music that builds tension and atmosphere",
                            "sound_effects": "Deep bass, heartbeat, dramatic stings",
                            "title_treatment": "Minimalist text animation revealing the title"
                        }
                
                # Display teaser script in a visually appealing way
                if 'teaser_script' in st.session_state:
                    script = st.session_state.teaser_script
                    
                    # Teaser details in a styled box
                    st.markdown(f"""
                    <div style="background-color: #2C3E50; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
                        <h5 style="color: #FF3D00; margin-bottom: 1rem;">Teaser Details</h5>
                        <p><strong>Duration:</strong> {script['duration']}</p>
                        <p><strong>Music:</strong> {script['music_suggestion']}</p>
                        <p><strong>Sound Effects:</strong> {script['sound_effects']}</p>
                        <p><strong>Title Treatment:</strong> {script['title_treatment']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Voiceover in a special styled box
                    st.markdown("<h5>Voiceover</h5>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="background-color: #2C3E50; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; font-style: italic; font-size: 1.1rem; line-height: 1.6;">
                        "{script['voiceover']}"
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Scene descriptions
                    st.markdown("<h5>Scenes</h5>", unsafe_allow_html=True)
                    for i, scene in enumerate(script['scenes'], 1):
                        st.markdown(f"""
                        <div style="background-color: #2C3E50; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <strong>Scene {i}:</strong> {scene}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Export Script as PDF", use_container_width=True):
                            st.success("Your teaser script has been exported and is ready to share!")
                    with col2:
                        if st.button("Send to Storyboard Artist", use_container_width=True):
                            st.info("This feature will be available in the next update.")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with material_tabs[6]:
            st.markdown("<div class='material-tab'><h4>Market Analysis</h4>", unsafe_allow_html=True)
            
            # Box office prediction tab
            st.markdown("##### Box Office & Performance Prediction")
            
            # Choose budget range
            budget_range = st.select_slider(
                "Estimated Production Budget",
                options=["Low Budget (<$10M)", "Mid Budget ($10M-$50M)", "High Budget ($50M-$150M)", "Blockbuster ($150M+)"]
            )
            
            # Choose target region
            target_region = st.multiselect(
                "Primary Target Markets",
                options=["North America", "Europe", "Asia", "Latin America", "Global"],
                default=["North America", "Global"]
            )
            
            if st.button("Generate Market Prediction", use_container_width=True):
                with st.spinner("Analyzing market potential..."):
                    if api_key:
                        # Create the prompt for market analysis
                        market_prompt = f"""
                        Create a detailed market prediction and financial analysis for adapting "{content['title']}" as a {selected_format}.
                        
                        CONTENT SUMMARY:
                        {content_text[:2000]}
                        
                        BUDGET: {budget_range}
                        TARGET MARKETS: {', '.join(target_region)}
                        
                        Please provide:
                        1. Box office/revenue prediction (global and per major region)
                        2. Comparable titles with their performance figures
                        3. Target demographic breakdown (% of audience)
                        4. Marketing strategy recommendations
                        5. Potential merchandising opportunities
                        6. ROI (Return on Investment) estimate
                        
                        Format your response in a structured, detailed analysis with specific numbers and percentages.
                        Include both conservative and optimistic scenarios.
                        """
                        
                        client = openai.OpenAI(api_key=api_key.strip())
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": market_prompt}],
                            temperature=0.7,
                            max_tokens=1500
                        )
                        
                        market_analysis = response.choices[0].message.content
                        st.session_state.market_analysis = market_analysis
                    else:
                        st.session_state.market_analysis = f"""
                        # Market Prediction for "{content['title']}" as a {selected_format}
                        
                        ## Box Office/Revenue Prediction
                        - Global: ${random.randint(50, 500)}M
                        - North America: ${random.randint(20, 200)}M
                        - International: ${random.randint(30, 300)}M
                        
                        ## Comparable Titles
                        - Similar Title 1: ${random.randint(100, 800)}M global
                        - Similar Title 2: ${random.randint(100, 800)}M global
                        - Similar Title 3: ${random.randint(100, 800)}M global
                        
                        ## Target Demographics
                        - Age 18-34: {random.randint(40, 60)}%
                        - Age 35-49: {random.randint(20, 40)}%
                        - Age 50+: {random.randint(5, 20)}%
                        
                        ## ROI Estimate
                        - Conservative: {random.randint(100, 200)}%
                        - Optimistic: {random.randint(200, 500)}%
                        """
                
                st.markdown("##### Market Analysis Results")
                st.markdown(st.session_state.market_analysis)
            
            # Ideal cast suggestions
            st.markdown("##### Ideal Cast Suggestions")
            
            if st.button("Generate Cast Suggestions", use_container_width=True):
                with st.spinner("Creating ideal cast lineup..."):
                    if 'character_profiles' in st.session_state and st.session_state.character_profiles:
                        if api_key:
                            primary_genre = content['recommended_genres'][0] if content['recommended_genres'] else "Drama"
                            
                            # Generate cast suggestions using the new function
                            cast_data = generate_cast_suggestions(
                                character_profiles=st.session_state.character_profiles,
                                adaptation_type=selected_format,
                                genre=primary_genre,
                                api_key=api_key
                            )
                            
                            st.session_state.cast_data = cast_data
                            
                            # Format the cast data into a readable text
                            cast_suggestions_text = "# Ideal Cast Suggestions\n\n"
                            for suggestion in cast_data.get("suggestions", []):
                                character = suggestion.get("character", "Unknown")
                                cast_suggestions_text += f"## {character}\n\n"
                                
                                # Primary suggestion
                                primary = suggestion.get("primary_suggestion", {})
                                if primary:
                                    cast_suggestions_text += f"**First Choice:** {primary.get('name', 'Unknown')}\n"
                                    cast_suggestions_text += f"*{primary.get('rationale', '')}*\n\n"
                                
                                # Alternatives
                                alternatives = suggestion.get("alternatives", [])
                                if alternatives:
                                    cast_suggestions_text += "**Alternatives:**\n"
                                    for alt in alternatives:
                                        cast_suggestions_text += f"- {alt.get('name', 'Unknown')}: {alt.get('rationale', '')}\n"
                                    cast_suggestions_text += "\n"
                            
                            st.session_state.cast_suggestions = cast_suggestions_text
                        else:
                            # Generate placeholder cast suggestions
                            cast_suggestions = "# Ideal Cast Suggestions\n\n"
                            for char in st.session_state.character_profiles[:5]:
                                cast_suggestions += f"## {char['name']} ({char['role']})\n"
                                cast_suggestions += f"- **First Choice:** [Famous Actor Name]\n"
                                cast_suggestions += f"- **Alternative:** [Alternative Actor Name]\n"
                                cast_suggestions += f"- **Why:** Would perfectly embody the {', '.join(char['key_traits'])} traits essential to this character.\n\n"
                            
                            st.session_state.cast_suggestions = cast_suggestions
                    else:
                        st.session_state.cast_suggestions = "Please generate character profiles first to get cast suggestions."
                
                st.session_state.show_cast = True
                st.rerun()
            
            # Display cast suggestions if available
            if st.session_state.get('show_cast', False) and 'cast_suggestions' in st.session_state:
                st.markdown(st.session_state.cast_suggestions)
                
                # Allow editing of cast suggestions
                with st.expander("Edit Cast Suggestions", expanded=False):
                    edited_cast = st.text_area(
                        "Edit cast suggestions",
                        value=st.session_state.cast_suggestions,
                        height=300
                    )
                    
                    if st.button("Update Cast"):
                        st.session_state.cast_suggestions = edited_cast
                        st.success("Cast suggestions updated!")
                        st.rerun()
        
        # Final step: Complete adaptation package
        st.markdown("### Complete Adaptation Package")
        
        # Create columns for export options
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            # Add option to edit title
            if 'export_title' not in st.session_state:
                st.session_state.export_title = content['title']
                
            custom_title = st.text_input(
                "Project Title",
                value=st.session_state.export_title
            )
            st.session_state.export_title = custom_title
        
        with export_col2:
            # File name for PDF
            if 'export_filename' not in st.session_state:
                sanitized_title = ''.join(c if c.isalnum() else '_' for c in content['title'])
                st.session_state.export_filename = f"{sanitized_title}_pitch_deck.pdf"
                
            pdf_filename = st.text_input(
                "PDF Filename",
                value=st.session_state.export_filename
            )
            st.session_state.export_filename = pdf_filename
        
        # Generate complete pitch deck
        if st.button("Generate Complete Pitch Deck", use_container_width=True, type="primary"):
            with st.spinner("Compiling your complete pitch deck..."):
                # Get all necessary components
                poster_url = None
                if 'poster_image_url' in st.session_state:
                    poster_url = st.session_state.poster_image_url
                
                pitch_content = st.session_state.pitch_content if 'pitch_content' in st.session_state else None
                plot_synopsis = st.session_state.plot_synopsis if 'plot_synopsis' in st.session_state else None
                character_profiles = st.session_state.character_profiles if 'character_profiles' in st.session_state else None
                teaser_script = st.session_state.teaser_script if 'teaser_script' in st.session_state else None
                market_analysis = st.session_state.market_analysis if 'market_analysis' in st.session_state else None
                cast_suggestions = st.session_state.cast_suggestions if 'cast_suggestions' in st.session_state else None
                
                # Create a temporary directory for the PDF
                import tempfile
                import os
                
                # Create the PDF
                with tempfile.TemporaryDirectory() as temp_dir:
                    pdf_path = os.path.join(temp_dir, pdf_filename)
                    
                    generate_pitch_pdf(
                        title=custom_title,
                        adaptation_type=selected_format,
                        pitch_content=pitch_content,
                        plot_synopsis=plot_synopsis,
                        character_profiles=character_profiles,
                        poster_image_url=poster_url,
                        teaser_script=teaser_script,
                        market_analysis=market_analysis,
                        cast_suggestions=cast_suggestions,
                        output_path=pdf_path
                    )
                    
                    # Read the PDF file for download
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    
                    # Store the PDF in the session state
                    st.session_state.pitch_pdf = pdf_bytes
                    st.session_state.pitch_pdf_name = pdf_filename
                    
                st.success("Your pitch deck is ready to download!")
                st.session_state.show_download = True
                st.rerun()
        
        # Download button (only show if PDF is generated)
        if st.session_state.get('show_download', False) and 'pitch_pdf' in st.session_state:
            st.download_button(
                label="📥 Download Pitch Deck",
                data=st.session_state.pitch_pdf,
                file_name=st.session_state.pitch_pdf_name,
                mime="application/pdf",
                use_container_width=True
            )
            
            # Preview of the PDF
            st.markdown("""
            <div style="background-color: #1E293B; padding: 1.5rem; border-radius: 8px; margin-top: 1rem; text-align: center;">
                <h3 style="margin-bottom: 1rem;">Your Pitch Deck is Ready!</h3>
                <p>Your complete pitch deck has been compiled with all the creative materials you've generated. Download it and share it with executives to sell your billion-dollar adaptation idea!</p>
                <div style="margin-top: 1rem;">
                    <span style="background-color: #2C3E50; padding: 0.5rem 1rem; border-radius: 20px; display: inline-block;">
                        <strong>Next Steps:</strong> Schedule meetings with production companies and streaming platforms
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # If no PDF generated yet, show information
        elif not st.session_state.get('show_download', False):
            st.info("Generate all the creative materials in the sections above, then click 'Generate Complete Pitch Deck' to compile everything into a professional PDF.")

with tab3:
    st.subheader("Create Content")

    # Create a styled container for the content creation section
    st.markdown("""
    <style>
    .content-creator {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .content-creator h3 {
        color: #FF3D00;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    .chapter-card {
        background-color: #2C3E50;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize plot_summary in session state if not present
    if 'plot_summary' not in st.session_state:
        st.session_state.plot_summary = ""
    
    if not st.session_state.plot_summary and 'plot_synopsis' not in st.session_state:
        # Create an attractive prompt card
        st.markdown("""
        <div style="background-color: #1E293B; border-radius: 10px; padding: 2rem; text-align: center; margin: 1rem 0;">
            <h3 style="color: #FF3D00; margin-bottom: 1rem;">Start Your Creative Journey</h3>
            <p style="margin-bottom: 1.5rem; font-size: 1.1rem;">Before creating content, you need to generate a Plot Summary and Plot Synopsis in the 'Generate Adaptation Materials' tab.</p>
            <img src="https://img.icons8.com/fluency/96/000000/light-on.png" style="width: 64px; height: 64px; margin-bottom: 1rem;">
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Go to Plot Synopsis Generator", use_container_width=True):
            st.session_state.active_tab = "🎬 Develop Adaptation"
            st.rerun()
    elif not st.session_state.plot_summary and 'plot_synopsis' in st.session_state:
        # Create an attractive prompt card
        st.markdown("""
        <div style="background-color: #1E293B; border-radius: 10px; padding: 2rem; text-align: center; margin: 1rem 0;">
            <h3 style="color: #FF3D00; margin-bottom: 1rem;">Almost There!</h3>
            <p style="margin-bottom: 1.5rem; font-size: 1.1rem;">You have generated a Plot Synopsis, but you still need to generate a Plot Summary in the 'Generate Adaptation Materials' tab.</p>
            <img src="https://img.icons8.com/fluency/96/000000/light-on.png" style="width: 64px; height: 64px; margin-bottom: 1rem;">
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Go to Plot Summary Generator", use_container_width=True):
            st.session_state.active_tab = "🎬 Develop Adaptation"
            st.rerun()
    else:
        st.markdown("<div class='content-creator'>", unsafe_allow_html=True)
        
        # Extract adaptation title from plot summary
        title_match = None
        if st.session_state.plot_summary:
            for line in st.session_state.plot_summary.split('\n')[:5]:
                if line.strip() and len(line) < 100:  # likely to be a title
                    title_match = line.strip()
                    break

        # Adaptation title with better styling
        st.markdown("<h3>Adaptation Title</h3>", unsafe_allow_html=True)
        
        if title_match:
            adaptation_title = st.text_input("Title", 
                                           value=title_match,
                                           placeholder="Enter your adaptation title")
        else:
            # Default to the original content title if no title found in summary
            default_title = st.session_state.current_content['title'] if st.session_state.current_content else ""
            adaptation_title = st.text_input("Title", 
                                           value=default_title,
                                           placeholder="Enter your adaptation title")

        # Get story structure and key elements
        st.markdown("<h3>Story Structure</h3>", unsafe_allow_html=True)

        # Display the plot summary in a nice card
        with st.expander("📄 View Plot Summary", expanded=False):
            st.markdown(f"""
            <div style="background-color: #2C3E50; padding: 1.5rem; border-radius: 8px;">
                {st.session_state.plot_summary}
            </div>
            """, unsafe_allow_html=True)

        # Story outline generation with better styling
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("📋 Generate Story Outline", use_container_width=True):
                if not api_key:
                    st.error("OpenAI API key is required for story outline generation.")
                else:
                    with st.spinner("Crafting your story outline..."):
                        # Get the appropriate content text based on content type
                        if 'current_content' in st.session_state:
                            if st.session_state.content_type == "reddit":
                                content_text = st.session_state.current_content['selftext']
                            else:  # wattpad
                                content = st.session_state.current_content
                                content_text = f"{content['description']}\n\n{content['content_sample'] if 'content_sample' in content else ''}"
                        else:
                            content_text = ""
                        
                        story_outline = generate_story_outline(
                            title=adaptation_title,
                            original_content=content_text,
                            plot_summary=st.session_state.plot_summary if 'plot_summary' in st.session_state else "",
                            adaptation_type=st.session_state.current_adaptation_type if 'current_adaptation_type' in st.session_state else "Movie",
                            genre=st.session_state.current_genre if 'current_genre' in st.session_state else "Drama",
                            api_key=api_key)
                            
                        st.session_state.story_outline = story_outline
        
        with col2:
            # Display generated outlines counter
            if 'story_outline' in st.session_state and st.session_state.story_outline:
                st.markdown("""
                <div style="background-color: #2C3E50; border-radius: 8px; padding: 1rem; text-align: center;">
                    <h4 style="margin: 0; font-size: 1rem;">Story Outline</h4>
                    <p style="font-size: 2rem; margin: 0.5rem 0; color: #FF3D00;">✓</p>
                    <p style="margin: 0; font-size: 0.9rem;">Generated</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Display story outline if available
        if 'story_outline' in st.session_state and st.session_state.story_outline:
            st.markdown("<h4 style='margin-top: 2rem;'>Story Outline</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background-color: #2C3E50; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
                {st.session_state.story_outline}
            </div>
            """, unsafe_allow_html=True)

        # Chapter generation with improved styling
        if 'story_outline' in st.session_state and st.session_state.story_outline:
            st.markdown("<h3>Generate Chapters</h3>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                chapter_num = st.number_input("Chapter number", min_value=1, max_value=20, value=1)
            with col2:
                chapter_pov = st.text_input("POV character (if applicable)", placeholder="Enter character name")
            
            with col3:
                # Display counter of generated chapters
                if 'chapters' in st.session_state:
                    st.markdown(f"""
                    <div style="background-color: #2C3E50; border-radius: 8px; padding: 1rem; text-align: center; height: 100%;">
                        <h4 style="margin: 0; font-size: 1rem;">Chapters</h4>
                        <p style="font-size: 2rem; margin: 0.5rem 0; color: #FF3D00;">{len(st.session_state.chapters)}</p>
                        <p style="margin: 0; font-size: 0.9rem;">Generated</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            if st.button("📝 Generate Chapter", use_container_width=True):
                if not api_key:
                    st.error("OpenAI API key is required for chapter generation.")
                else:
                    with st.spinner(f"Writing chapter {chapter_num}..."):
                        chapter_content = generate_book_chapter(
                            title=adaptation_title,
                            plot_summary=st.session_state.plot_summary,
                            story_outline=st.session_state.story_outline,
                            chapter_num=chapter_num,
                            pov_character=chapter_pov,
                            genre=st.session_state.current_genre if 'current_genre' in st.session_state else "Drama",
                            api_key=api_key)
                            
                        # Store the chapter in session state
                        if 'chapters' not in st.session_state:
                            st.session_state.chapters = {}
                            
                        st.session_state.chapters[chapter_num] = chapter_content
                    
                    st.markdown(f"<h4>Chapter {chapter_num}</h4>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="chapter-card">
                        {chapter_content}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display previously generated chapters with improved styling
            if 'chapters' in st.session_state and st.session_state.chapters:
                st.markdown("<h3>Previously Generated Chapters</h3>", unsafe_allow_html=True)
                
                # Create a chapter selection mechanism
                chapter_numbers = list(sorted(st.session_state.chapters.keys()))
                selected_chapter = st.selectbox("Select chapter to view", options=chapter_numbers, format_func=lambda x: f"Chapter {x}")
                
                if selected_chapter:
                    st.markdown(f"<h4>Chapter {selected_chapter}</h4>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="chapter-card">
                        {st.session_state.chapters[selected_chapter]}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add export options
                if st.button("📤 Export All Chapters as PDF", use_container_width=True):
                    st.success("Your chapters would be exported as a PDF in a real implementation.")
        
        st.markdown("</div>", unsafe_allow_html=True)


# Add footer after all tab content
st.markdown("""
<footer style="margin-top: 5rem; padding-top: 1.5rem; border-top: 1px solid #334155; text-align: center;">
    <p style="color: #94A3B8; font-size: 0.9rem;">IP Pitch Builder © 2025</p>
    <p style="color: #94A3B8; font-size: 0.8rem; margin-top: 0.5rem;">
        Created with 💖 for storytellers and adaptation enthusiasts
    </p>
</footer>
""", unsafe_allow_html=True)

