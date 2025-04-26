import openai
import re
import json

def evaluate_adaptation_potential(title, content, score, num_comments, api_key):
    """
    Evaluates the adaptation potential of a Reddit post using OpenAI
    
    Args:
        title (str): Post title
        content (str): Post content
        score (int): Post upvotes
        num_comments (int): Number of comments
        api_key (str): OpenAI API key
        
    Returns:
        dict: Adaptation analysis including score, justification, recommended genres, and similar works
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return {
            "score": 5.0,
            "justification": "API key is missing or appears to be invalid. Please provide a valid OpenAI API key to get detailed analysis.",
            "recommended_genres": ["Drama"],
            "similar_works": ["Analysis not available without valid API key"],
            "adaptation_type": "Movie",
            "key_elements": ["Character development", "Plot", "Setting"],
            "target_audience": "General audience"
        }
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = content[:3000] + ("..." if len(content) > 3000 else "")
        
        # Construct prompt
        prompt = f"""
        Analyze this Reddit post for its potential to be adapted into a movie, TV show, or book.
        
        TITLE: {title}
        
        CONTENT: {content_preview}
        
        ENGAGEMENT: {score} upvotes, {num_comments} comments
        
        Score this post's adaptation potential on a scale of 1-10, where:
        1 = Not adaptable at all
        10 = Exceptional adaptation potential
        
        Provide your analysis in JSON format with these fields:
        - score: (number between 1-10, can use decimals)
        - justification: (detailed explanation of why this would make a good adaptation)
        - recommended_genres: (array of 3-5 genres that would work well for this adaptation)
        - similar_works: (array of 3-5 similar movies, TV shows, or books that share thematic elements)
        - adaptation_type: (string, either "Movie", "TV Series", "Novel", or "Short Story" - which format would work best)
        - key_elements: (array of 3-5 narrative elements that make this story compelling)
        - target_audience: (string describing the ideal audience for this adaptation)
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        # Parse the response
        result = json.loads(response.choices[0].message.content)
        
        # Extract the data with defaults for missing fields
        adaptation_data = {
            "score": float(result.get("score", 5.0)),
            "justification": result.get("justification", "No justification provided"),
            "recommended_genres": result.get("recommended_genres", ["Drama"]),
            "similar_works": result.get("similar_works", ["No similar works identified"]),
            "adaptation_type": result.get("adaptation_type", "Movie"),
            "key_elements": result.get("key_elements", ["Character development", "Plot", "Setting"]),
            "target_audience": result.get("target_audience", "General audience")
        }
        
        return adaptation_data
    
    except Exception as e:
        error_message = str(e)
        # Check for common API errors
        if "invalid_api_key" in error_message or "Invalid API key" in error_message:
            error_details = "The OpenAI API key provided is invalid. Please check your API key and try again."
        elif "rate_limit_exceeded" in error_message:
            error_details = "OpenAI API rate limit exceeded. Please try again later."
        elif "insufficient_quota" in error_message:
            error_details = "Your OpenAI API account has insufficient quota. Please check your usage or billing information."
        elif "invalid auth" in error_message.lower() or "authentication" in error_message.lower():
            error_details = "Authentication error with OpenAI API. Your key may be expired or invalid."
        else:
            error_details = f"Error connecting to OpenAI API: {error_message}"
        
        # Print the error to the console for debugging
        print(f"OpenAI API Error: {error_message}")
            
        # In case of API error, return default values with consistent types
        return {
            "score": 5.0,
            "justification": error_details,
            "recommended_genres": ["Drama"],
            "similar_works": ["Error retrieving similar works"],
            "adaptation_type": "Movie",
            "key_elements": ["Unknown due to error"],
            "target_audience": "General audience"
        }
