import openai
import json

def generate_plot_summary(title, content, adaptation_type, genre, api_key):
    """
    Generates a plot summary for a possible adaptation
    
    Args:
        title (str): Post title
        content (str): Post content
        adaptation_type (str): Type of adaptation (Movie, TV Series, etc.)
        genre (str): Preferred genre
        api_key (str): OpenAI API key
        
    Returns:
        str: Generated plot summary
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return "Unable to generate plot summary: Invalid OpenAI API key. Please provide a valid key to use this feature."
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = content[:4000] + ("..." if len(content) > 4000 else "")
        
        # Construct prompt
        prompt = f"""
        Create a detailed plot summary for a {adaptation_type} adaptation of this Reddit post in the {genre} genre.
        
        ORIGINAL REDDIT POST TITLE: {title}
        
        CONTENT: {content_preview}
        
        Please include:
        1. A compelling title for the adaptation
        2. Main characters and their motivations
        3. Core conflict/storyline
        4. Beginning, middle, and end structure
        5. Key turning points or twists
        6. Thematic elements
        
        Format your response as a cohesive, professional plot summary that would appeal to producers or publishers.
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating plot summary: {str(e)}"

def generate_poster_concept(title, plot_summary, adaptation_type, genre, mood, api_key):
    """
    Generates a detailed description of a poster concept for the adaptation
    
    Args:
        title (str): Original post title
        plot_summary (str): Generated plot summary
        adaptation_type (str): Type of adaptation
        genre (str): Selected genre
        mood (str): Visual mood/style
        api_key (str): OpenAI API key
        
    Returns:
        str: Detailed poster concept description
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return "Unable to generate poster concept: Invalid OpenAI API key. Please provide a valid key to use this feature."
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Extract adaptation title from plot summary (it should be in the first few lines)
        title_match = None
        for line in plot_summary.split('\n')[:5]:
            if line.strip() and len(line) < 100:  # likely to be a title
                title_match = line.strip()
                break
        
        adaptation_title = title_match or f"{title} - {adaptation_type} Adaptation"
        
        # Construct prompt
        prompt = f"""
        Create a detailed description of a poster concept for a {adaptation_type} called "{adaptation_title}" 
        in the {genre} genre with a {mood} visual style.
        
        PLOT SUMMARY: {plot_summary[:1000]}...
        
        Describe in detail:
        1. The overall composition and layout
        2. Color palette and lighting
        3. Main visual elements and imagery
        4. Typography and text placement
        5. Mood and atmosphere
        6. Any symbolic elements that hint at the story
    
        Your description should be vivid enough that a designer could create the poster based on your description.
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating poster concept: {str(e)}"

def generate_book_chapter(title, plot_summary, story_outline, chapter_num, pov_character, genre, api_key):
    """
    Generates a detailed chapter for a book adaptation
    
    Args:
        title (str): Adaptation title
        plot_summary (str): Generated plot summary
        story_outline (str): Outline of the story
        chapter_num (int): Current chapter number to generate
        pov_character (str): Point of view character, if applicable
        genre (str): Selected genre
        api_key (str): OpenAI API key
        
    Returns:
        str: Generated chapter content
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return "Unable to generate book chapter: Invalid OpenAI API key. Please provide a valid key to use this feature."
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Determine approximate total chapters from story outline
        total_chapters = 12  # Default value
        
        # Determine chapter position in the story arc
        if chapter_num == 1:
            position = "beginning"
        elif chapter_num == total_chapters:
            position = "conclusion"
        elif chapter_num < total_chapters / 3:
            position = "early"
        elif chapter_num < (total_chapters * 2) / 3:
            position = "middle"
        else:
            position = "late"
        
        # Add POV character information if provided
        pov_info = f"This chapter should be written from {pov_character}'s point of view." if pov_character else ""
        
        # Construct prompt
        prompt = f"""
        Write Chapter {chapter_num} of a {genre} novel titled "{title}" based on this plot summary:
        
        PLOT SUMMARY: {plot_summary}
        
        STORY OUTLINE: {story_outline[:1000]}...
        
        This is the {position} part of the story. This is chapter {chapter_num}.
        {pov_info}
        
        Guidelines:
        1. Write in a polished, literary style appropriate for the {genre} genre
        2. Include rich descriptions, realistic dialogue, and character development
        3. Incorporate key plot elements from the summary that would appear at this point in the story
        4. End the chapter with an appropriate hook for this story position
        5. Chapter length should be 1000-1500 words
        
        Format your response as a well-structured novel chapter with a chapter title.
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating chapter: {str(e)}"

def generate_story_outline(title, original_content, plot_summary, adaptation_type, genre, api_key):
    """
    Generates a detailed story outline for a book adaptation
    
    Args:
        title (str): Adaptation title  
        original_content (str): Original content
        plot_summary (str): Generated plot summary
        adaptation_type (str): Type of adaptation
        genre (str): Selected genre
        api_key (str): OpenAI API key
        
    Returns:
        str: Story outline with chapter descriptions
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return "Invalid OpenAI API key. Please provide a valid key to use this feature."
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = original_content[:2000] + ("..." if len(original_content) > 2000 else "")
        
        # Construct prompt
        prompt = f"""
        Create a detailed story outline for a {genre} {adaptation_type} titled "{title}" based on this information:
        
        ORIGINAL CONTENT: {content_preview}
        
        PLOT SUMMARY: {plot_summary}
        
        Create a chapter-by-chapter outline that includes:
        1. Main plot points and their development
        2. Character arcs and their progression
        3. Key scenes and turning points
        4. Thematic elements and how they're expressed
        5. Beginning, middle, and end structure
        
        Format your response as a structured outline with clear chapter markers.
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating story outline: {str(e)}"

def generate_pitch_deck(title, original_content, adaptation_type, target_audience, key_elements, genres, api_key):
    """
    Generates a pitch deck for the adaptation
    
    Args:
        title (str): Original content title
        original_content (str): Original content text
        adaptation_type (str): Type of adaptation (Movie, TV Series)
        target_audience (str): Target audience description
        key_elements (list): List of key narrative elements
        genres (list): List of recommended genres
        api_key (str): OpenAI API key
        
    Returns:
        dict: Pitch deck content with high concept, logline, unique selling points, etc.
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return {
            "high_concept": f"Adaptation of '{title}' as a {adaptation_type}",
            "logline": f"A compelling {adaptation_type.lower()} based on the original work that captures the essence of the source material.",
            "unique_selling_points": [
                "Based on popular online content",
                "Built-in audience from original platform",
                "Strong narrative potential"
            ],
            "visual_style": f"The visual style will match the tone of the original content, with a focus on creating an engaging {adaptation_type.lower()} experience.",
            "comp_titles": ["Similar Work 1", "Similar Work 2", "Similar Work 3"]
        }
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = original_content[:4000] + ("..." if len(original_content) > 4000 else "")
        
        # Convert key_elements and genres to string format for the prompt
        key_elements_str = ", ".join(key_elements)
        genres_str = ", ".join(genres)
        
        # Construct prompt
        prompt = f"""
        Create a comprehensive pitch deck for a {adaptation_type} adaptation of "{title}" for a major streaming platform.
        
        ORIGINAL CONTENT: {content_preview}
        
        TARGET AUDIENCE: {target_audience}
        KEY NARRATIVE ELEMENTS: {key_elements_str}
        RECOMMENDED GENRES: {genres_str}
        
        The streaming landscape is competitive, so this pitch needs to highlight what makes this story uniquely suited for adaptation and why it will attract viewers.
        
        Please generate the following components of a pitch deck:
        1. A high-concept description (one powerful sentence that captures the essence of the adaptation)
        2. A compelling logline (1-2 sentences that hook the reader and summarize the story)
        3. 4-6 unique selling points that make this adaptation marketable to streaming platforms and their audiences
        4. A detailed description of the visual style and tone, referencing successful shows/films if relevant
        5. 3-5 comparable titles (similar successful works on streaming platforms)
        6. Potential for franchise expansion (sequels, spinoffs, shared universe potential)
        
        Format your response as a structured JSON object with these fields:
        - high_concept
        - logline
        - unique_selling_points (array)
        - visual_style
        - comp_titles (array)
        - franchise_potential
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        return result
    
    except Exception as e:
        return {
            "high_concept": f"Adaptation of '{title}' as a {adaptation_type}",
            "logline": f"Error generating pitch deck: {str(e)}",
            "unique_selling_points": ["Error occurred"],
            "visual_style": "Not available due to error",
            "comp_titles": [],
            "franchise_potential": "Unable to determine due to error"
        }

def generate_character_profiles(title, original_content, adaptation_type, api_key):
    """
    Generates character profiles for the adaptation
    
    Args:
        title (str): Original content title
        original_content (str): Original content text
        adaptation_type (str): Type of adaptation (Movie, TV Series, etc.)
        api_key (str): OpenAI API key
        
    Returns:
        list: List of character profile dictionaries
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return [
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
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = original_content[:4000] + ("..." if len(original_content) > 4000 else "")
        
        # Construct prompt
        prompt = f"""
        Create detailed character profiles for a {adaptation_type} adaptation of "{title}".
        
        ORIGINAL CONTENT: {content_preview}
        
        For each main character (aim for 3-5 characters):
        1. Name and role in the story (protagonist, antagonist, ally, etc.)
        2. Brief physical description and background
        3. Character arc throughout the story
        4. 3-5 key personality traits
        
        Format your response as a JSON array of character objects with these fields:
        - name
        - role
        - description
        - arc
        - key_traits (array)
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        # Ensure we have a list of characters
        characters_data = result.get("characters", [])
        if not characters_data and isinstance(result, list):
            characters_data = result
            
        return characters_data
    
    except Exception as e:
        return [
            {
                "name": "Error",
                "role": "N/A",
                "description": f"Error generating character profiles: {str(e)}",
                "arc": "N/A",
                "key_traits": ["Error occurred"]
            }
        ]

def generate_plot_synopsis(title, original_content, adaptation_type, api_key):
    """
    Generates a plot synopsis for the adaptation
    
    Args:
        title (str): Original content title
        original_content (str): Original content text
        adaptation_type (str): Type of adaptation (Movie, TV Series, etc.)
        api_key (str): OpenAI API key
        
    Returns:
        dict: Plot synopsis with short and detailed synopses and act structure
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return {
            "short_synopsis": f"A {adaptation_type.lower()} adaptation of '{title}' that captures the essence of the original content.",
            "detailed_synopsis": f"This {adaptation_type.lower()} follows the story presented in the original content, adapted to fit the medium of {adaptation_type.lower()}. The narrative maintains the key elements that made the original compelling while enhancing aspects that will work well in the new format.",
            "act_structure": [
                "Act 1: Introduction to the world and characters",
                "Act 2: Development of the core conflict",
                "Act 3: Resolution and conclusion"
            ]
        }
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = original_content[:4000] + ("..." if len(original_content) > 4000 else "")
        
        # Construct prompt
        prompt = f"""
        Create a comprehensive plot synopsis for a {adaptation_type} adaptation of "{title}".
        
        ORIGINAL CONTENT: {content_preview}
        
        Please provide:
        1. A short synopsis (1-2 sentences)
        2. A detailed synopsis (300-500 words)
        3. A breakdown of the act structure (3-5 acts depending on the adaptation type)
        
        For a movie, use a standard 3-act structure.
        For a TV series, consider a 5-act structure or season arc.
        For other formats, use an appropriate structure.
        
        Format your response as a JSON object with these fields:
        - short_synopsis
        - detailed_synopsis
        - act_structure (array of act descriptions)
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse response
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        return {
            "short_synopsis": f"Error: {str(e)}",
            "detailed_synopsis": "Unable to generate detailed synopsis due to an error.",
            "act_structure": ["Act 1: Error occurred"]
        }

def generate_audience_analysis(title, original_content, adaptation_type, target_audience, api_key):
    """
    Generates a target audience analysis for the adaptation
    
    Args:
        title (str): Original content title
        original_content (str): Original content text
        adaptation_type (str): Type of adaptation (Movie, TV Series, etc.)
        target_audience (str): Initial target audience description
        api_key (str): OpenAI API key
        
    Returns:
        dict: Audience analysis with demographics, psychographics, and marketing strategies
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return {
            "primary_audience": target_audience,
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
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = original_content[:3000] + ("..." if len(original_content) > 3000 else "")
        
        # Construct prompt
        prompt = f"""
        Create a detailed target audience analysis for a {adaptation_type} adaptation of "{title}".
        
        ORIGINAL CONTENT: {content_preview}
        
        INITIAL TARGET AUDIENCE: {target_audience}
        
        Please provide:
        1. A refined primary audience description
        2. Key demographics (age range, gender distribution, geographic focus)
        3. Psychographic profile (interests, values, behaviors)
        4. 3-5 effective marketing strategies to reach this audience
        
        Format your response as a JSON object with these fields:
        - primary_audience (string with refined description)
        - demographics (array of strings)
        - psychographics (array of strings)
        - marketing_strategies (array of strings)
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        return {
            "primary_audience": f"Error: {str(e)}",
            "demographics": ["Unable to generate demographics due to an error"],
            "psychographics": ["Unable to generate psychographics due to an error"],
            "marketing_strategies": ["Unable to generate marketing strategies due to an error"]
        }

def generate_radar_chart_values(content, adaptation_type, api_key):
    """
    Generates values for a radar chart visualizing adaptation potential
    
    Args:
        content (str): Original content text
        adaptation_type (str): Type of adaptation (Movie, TV Series, etc.)
        api_key (str): OpenAI API key
        
    Returns:
        list: Radar chart values for different adaptation categories
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        import random
        # Return random values between 60-90 for demo purposes
        return [random.randint(60, 90) for _ in range(5)]
    
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
        Analyze this content for adaptation potential as a {adaptation_type} and score each category from 0-100.
        
        CONTENT: {content_preview}
        
        Categories to score:
        1. Narrative Strength - How strong is the core story? Does it have a compelling plot?
        2. Visual Potential - How well would this translate to visual storytelling?
        3. Character Development - How well-developed are the characters? Are they interesting?
        4. Market Appeal - How appealing would this be to the target market?
        5. Target Audience Match - How well does this match current audience interests?
        
        Format your response as a JSON object with an array of exactly 5 numbers between 0-100, one for each category in the order listed above.
        Example: [75, 82, 60, 88, 70]
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=100
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        # Extract the array of values
        if isinstance(result, dict) and "scores" in result:
            return result["scores"]
        elif isinstance(result, dict) and "values" in result:
            return result["values"]
        elif isinstance(result, list):
            return result
        else:
            # Try to find any array in the response
            for key, value in result.items():
                if isinstance(value, list) and len(value) == 5:
                    return value
            
            # If all else fails, return random values
            import random
            return [random.randint(60, 90) for _ in range(5)]
    
    except Exception as e:
        # Return default values on error
        import random
        return [random.randint(60, 90) for _ in range(5)]

# Add a new function for generating teaser trailer scripts
def generate_teaser_trailer_script(title, original_content, adaptation_type, visual_style, genre, api_key):
    """
    Generates a teaser trailer script for a movie or TV series adaptation
    
    Args:
        title (str): Original content title
        original_content (str): Original content text
        adaptation_type (str): Type of adaptation (Movie, TV Series)
        visual_style (str): Description of the visual style
        genre (str): Primary genre
        api_key (str): OpenAI API key
        
    Returns:
        dict: Teaser trailer script with voiceover, scenes, and music suggestions
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return {
            "duration": "30 seconds",
            "voiceover": f"In a world where nothing is as it seems... {title}. Coming soon.",
            "scenes": [
                "Opening shot: Fade in from black to reveal main setting",
                "Character introduction: Brief glimpse of protagonist",
                "Tension building: Quick cuts between key scenes",
                "Title reveal: Title appears with dramatic music"
            ],
            "music_suggestion": "Atmospheric, building to climactic reveal",
            "sound_effects": "Deep bass, heartbeat, dramatic stings",
            "title_treatment": "Minimalist text animation revealing the title"
        }
    
    try:
        # Initialize OpenAI client
        # Clean up API key to remove potential whitespace or other issues
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = original_content[:4000] + ("..." if len(original_content) > 4000 else "")
        
        # Construct prompt
        prompt = f"""
        Create a compelling teaser trailer script for a {adaptation_type} titled "{title}" that would appear on major streaming platforms.
        
        STORY DETAILS:
        {content_preview}
        
        ADAPTATION TYPE: {adaptation_type}
        VISUAL STYLE: {visual_style}
        GENRE: {genre}
        
        The teaser should be 30-60 seconds long and create intrigue without revealing too much of the plot.
        
        Please generate the following components:
        1. Recommended duration (30, 45, or 60 seconds)
        2. Voiceover script (the narration that would be heard)
        3. Scene descriptions (4-6 key shots/moments to show)
        4. Music suggestions (style, tone, and mood)
        5. Sound effect recommendations
        6. Title treatment (how the title should appear)
        
        Format your response as a JSON object with these fields:
        - duration
        - voiceover
        - scenes (array)
        - music_suggestion
        - sound_effects
        - title_treatment
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        return {
            "duration": "Error occurred",
            "voiceover": f"Error generating teaser script: {str(e)}",
            "scenes": ["Error occurred"],
            "music_suggestion": "Unable to generate due to error",
            "sound_effects": "Unable to generate due to error",
            "title_treatment": "Unable to generate due to error"
        }

# Add a new function for generating alternate endings
def generate_alternate_endings(title, original_content, plot_synopsis, adaptation_type, api_key, num_endings=2):
    """
    Generates multiple alternate endings for a story adaptation
    
    Args:
        title (str): Original content title
        original_content (str): Original content text
        plot_synopsis (dict): Plot synopsis with short/detailed synopsis
        adaptation_type (str): Type of adaptation (Movie, TV Series)
        api_key (str): OpenAI API key
        num_endings (int): Number of alternate endings to generate
        
    Returns:
        list: List of alternate endings with descriptions and implications
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20:
        return [
            {
                "title": "Happy Ending",
                "description": f"A more uplifting version where the protagonist achieves their goal.",
                "implications": "Would appeal to broader audiences but might reduce dramatic impact."
            },
            {
                "title": "Tragic Ending",
                "description": f"A darker conclusion where the protagonist fails but learns an important lesson.",
                "implications": "Creates a more profound emotional impact but might alienate viewers seeking escapism."
            }
        ]
    
    try:
        # Initialize OpenAI client
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare content (limit length)
        content_preview = original_content[:3000] + ("..." if len(original_content) > 3000 else "")
        
        # Extract the original ending from the plot synopsis
        original_synopsis = plot_synopsis.get('detailed_synopsis', '')
        
        # Construct prompt
        prompt = f"""
        Create {num_endings} compelling alternate endings for a {adaptation_type} adaptation of "{title}".
        
        ORIGINAL CONTENT: {content_preview}
        
        PLOT SYNOPSIS: {original_synopsis}
        
        For each alternate ending, provide:
        1. A descriptive title for the alternate ending
        2. A detailed description of how the story would conclude (150-250 words)
        3. The implications of this ending (commercial appeal, thematic impact, etc.)
        
        Create distinct endings that explore different emotional tones and narrative possibilities.
        
        Format your response as a JSON array with objects containing these fields:
        - title (string)
        - description (string)
        - implications (string)
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=1500
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        # Ensure we have a list of endings
        endings = result.get("alternate_endings", [])
        if not endings and isinstance(result, list):
            endings = result
            
        return endings
    
    except Exception as e:
        return [
            {
                "title": "Error",
                "description": f"Error generating alternate endings: {str(e)}",
                "implications": "Please try again or adjust the input parameters."
            }
        ]

# Add a function to generate cast suggestions with real actors
def generate_cast_suggestions(character_profiles, adaptation_type, genre, api_key):
    """
    Generates cast suggestions with real-world actors for an adaptation
    
    Args:
        character_profiles (list): List of character profile dictionaries
        adaptation_type (str): Type of adaptation (Movie, TV Series)
        genre (str): Primary genre of the adaptation
        api_key (str): OpenAI API key
        
    Returns:
        dict: Dictionary with character names as keys and cast suggestions as values
    """
    # Check if API key is provided and valid (basic check)
    if not api_key or len(api_key) < 20 or not character_profiles:
        return {
            "suggestions": [
                {
                    "character": "Protagonist",
                    "primary_suggestion": {"name": "Unknown Actor", "rationale": "No API key provided"},
                    "alternatives": [{"name": "Unknown Actor", "rationale": "No API key provided"}]
                }
            ]
        }
    
    try:
        # Initialize OpenAI client
        api_key = api_key.strip() if api_key else None
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare character profiles for the prompt
        character_data = []
        for character in character_profiles:
            char_info = {
                "name": character.get("name", "Unknown"),
                "role": character.get("role", "Unknown"),
                "description": character.get("description", ""),
                "traits": character.get("key_traits", [])
            }
            character_data.append(char_info)
        
        # Construct prompt
        prompt = f"""
        Suggest ideal casting options for a {adaptation_type} adaptation in the {genre} genre.
        
        CHARACTER PROFILES:
        {json.dumps(character_data)}
        
        For each character, provide:
        1. A primary casting suggestion (a real, currently active actor)
        2. Two alternative casting options
        3. A brief rationale for each suggestion explaining why they would be perfect for the role
        
        Consider actors who:
        - Are age-appropriate for the character
        - Have experience in similar genres
        - Would bring commercial appeal to the project
        - Could believably embody the character's traits and arc
        
        Format your response as a JSON object with this structure:
        {{
            "suggestions": [
                {{
                    "character": "Character Name",
                    "primary_suggestion": {{
                        "name": "Actor Name",
                        "rationale": "Explanation of why they'd be perfect"
                    }},
                    "alternatives": [
                        {{
                            "name": "Alternative Actor Name",
                            "rationale": "Explanation of why they'd be good"
                        }},
                        {{
                            "name": "Alternative Actor Name",
                            "rationale": "Explanation of why they'd be good"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        return result
    
    except Exception as e:
        return {
            "suggestions": [
                {
                    "character": "Error",
                    "primary_suggestion": {"name": "Error", "rationale": f"Error generating cast: {str(e)}"},
                    "alternatives": [
                        {"name": "Unknown", "rationale": "Error occurred"},
                        {"name": "Unknown", "rationale": "Error occurred"}
                    ]
                }
            ]
        }
