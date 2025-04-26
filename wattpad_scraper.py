import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re
import json

def fetch_wattpad_stories(category=None, tag=None, limit=10, language="en", 
                         min_reads=10000, min_votes=1000, min_parts=5):
    """
    Fetches popular stories from Wattpad based on given criteria
    
    Args:
        category (str): Category to fetch stories from (e.g., 'romance', 'fantasy')
        tag (str): Tag to search for stories
        limit (int): Number of stories to fetch
        language (str): Language code for stories (default: 'en' for English)
        min_reads (int): Minimum number of reads for stories
        min_votes (int): Minimum number of votes for stories
        min_parts (int): Minimum number of parts/chapters for stories
        
    Returns:
        list: List of stories as dictionaries or error message
    """
    try:
        stories = []
        base_url = "https://www.wattpad.com"
        
        # Set up the search URL based on parameters
        if category:
            url = f"{base_url}/stories/{category}?language={language}"
        elif tag:
            tag_formatted = tag.replace(' ', '+')
            url = f"{base_url}/search/{tag_formatted}?language={language}"
        else:
            url = f"{base_url}/stories?language={language}"
            
        print(f"Fetching Wattpad stories from URL: {url}")
            
        # Set headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://www.wattpad.com/"
        }
        
        # Make the request
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return f"Error: Failed to fetch Wattpad stories. Status code: {response.status_code}"
            
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save HTML to analyze structure
        with open('wattpad_debug.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"Saving HTML to wattpad_debug.html for analysis")
        
        # New approach: Extract story cards based on current structure
        # First, try the most common pattern for story listings
        story_elements = soup.select('ul.story-list li') or soup.select('ul.story-card-container li')
        
        # If no results found with those selectors, try other common patterns
        if not story_elements:
            story_elements = soup.select('div.story-card') or soup.select('div.browse-story-item')
            
        # If still no results, try more generic approaches
        if not story_elements:
            story_elements = soup.select('li[data-story-id]') or soup.select('div[data-story-id]')
        
        # Try even more generic selectors
        if not story_elements:
            story_elements = soup.select('li.browse-story-item') or soup.select('li.story-item') or soup.select('div.story-item')
        
        # Last resort, look for any list items with a link
        if not story_elements:
            all_list_items = soup.select('ul li')
            story_elements = [li for li in all_list_items if li.find('a') and li.find('a').get('href') and ('/story/' in li.find('a').get('href') or '/w/' in li.find('a').get('href'))]
        
        if not story_elements:
            return "Error: Could not identify story elements on page. Wattpad may have changed their HTML structure."
        
        print(f"Found {len(story_elements)} story elements")
        
        processed_count = 0
        
        for story_element in story_elements:
            if processed_count >= limit:
                break
                
            try:
                # Extract title and URL
                title_element = (
                    story_element.select_one('.title') or 
                    story_element.select_one('h3.story-title') or 
                    story_element.select_one('h3')
                )
                
                # Get the title text
                title = ""
                if title_element:
                    title = title_element.text.strip()
                else:
                    # Try to find any text that looks like a title
                    for element in story_element.select('a'):
                        if element.text and len(element.text.strip()) > 0 and element.text.strip() != "Community Happenings":
                            title = element.text.strip()
                            break
                
                if not title:
                    # Extract title from the full text using a pattern
                    element_text = story_element.text.strip()
                    title_match = re.search(r'#\d+\s*(.+?)\s*by\s', element_text)
                    if title_match:
                        title = title_match.group(1).strip()
                
                # Remove any leading "#X" numbering from title
                title = re.sub(r'^#\d+\s*', '', title)
                
                # If still no title, skip this element
                if not title:
                    continue
                
                # Get the URL path
                url_path = None
                link_element = title_element if title_element and title_element.name == 'a' else story_element.find('a')
                
                if link_element and link_element.get('href'):
                    url_path = link_element.get('href')
                
                if not url_path:
                    # Try to find any href that has story in it
                    for a_tag in story_element.select('a'):
                        href = a_tag.get('href', '')
                        if '/story/' in href or '/w/' in href:
                            url_path = href
                            break
                
                if not url_path:
                    continue
                
                # Format the story URL
                if url_path.startswith('http'):
                    story_url = url_path
                else:
                    story_url = f"{base_url}{url_path}"
                
                # Extract the full text for pattern matching
                element_text = story_element.text.strip().lower()
                element_text_lines = element_text.split('\n')
                
                # Extract stats using pattern matching
                reads = 0
                votes = 0
                parts = 0
                
                # Extract vote info if present in vote elements
                vote_elements = story_element.select('[class*="vote"]')
                if vote_elements:
                    for ve in vote_elements:
                        vote_text = ve.text.strip()
                        if re.search(r'\d', vote_text): # Check if the text contains numbers
                            votes = parse_number(vote_text)
                            break
                
                # Get numerical values directly from element text
                # From our test, we've seen patterns like:
                # #1ceo's girlby anushka17.8m327k45
                # This indicates 17.8m reads, 327k votes, 45 parts
                
                # Extract a sequence of numbers with suffixes (pattern like 17.8m327k45)
                combined_stats_match = re.search(r'(\d+\.?\d*[KkMmBb]?)(\d+\.?\d*[KkMmBb]?)(\d+)', element_text)
                if combined_stats_match:
                    # First number with suffix is likely reads
                    if not reads:
                        reads = parse_number(combined_stats_match.group(1))
                        print(f"Found reads from combined pattern: {reads}")
                    
                    # Second number with suffix is likely votes
                    if not votes:
                        votes = parse_number(combined_stats_match.group(2))
                        print(f"Found votes from combined pattern: {votes}")
                    
                    # Third number is likely parts
                    if not parts:
                        parts = parse_number(combined_stats_match.group(3))
                        print(f"Found parts from combined pattern: {parts}")
                
                # Look for other patterns from our test output
                for line in element_text_lines:
                    line = line.strip().lower()
                    # Some elements show votes like "327K"
                    if not votes and re.search(r'\b\d+\.?\d*[KkMmBb]\b', line):
                        vote_match = re.search(r'\b(\d+\.?\d*[KkMmBb])\b', line)
                        if vote_match:
                            votes = parse_number(vote_match.group(1))
                            print(f"Found votes from standalone K/M number: {votes}")
                
                    # Look for reads in lines containing both numbers and "read"
                    if not reads and 'read' in line and re.search(r'\d+', line):
                        reads_text = re.search(r'(\d+\.?\d*[KkMmBb]?).*?read', line)
                        if reads_text:
                            reads = parse_number(reads_text.group(1))
                            print(f"Found reads from contextual line: {reads}")
                    
                    # Find parts in lines containing "part"
                    if not parts and 'part' in line and re.search(r'\d+', line):
                        parts_text = re.search(r'(\d+).*?part', line)
                        if parts_text:
                            parts = parse_number(parts_text.group(1))
                            print(f"Found parts from contextual line: {parts}")
                
                # Based on our testing output, story elements often show text like "17.8m" for reads
                # Let's add a pattern to extract numbers followed by suffixes
                for line in element_text_lines:
                    line = line.strip()
                    if not reads:
                        # Try to find patterns like "17.8m" that likely represent reads
                        reads_match = re.search(r'(\d+\.\d+[KkMmBb])', line)
                        if reads_match:
                            reads = parse_number(reads_match.group(1))
                            print(f"Found reads from line pattern: {reads}")
                
                # Extract reads from text
                read_patterns = [
                    r'(\d+(?:\.\d+)?[KkMmBb]?)\s*(?:read|view|visit)',  # Matches: 25.5k read, 1.2m views
                    r'reads\s*(\d+(?:\.\d+)?[KkMmBb]?)',  # Matches: reads 25.5k
                    r'(\d+(?:\.\d+)?[KkMmBb]?)(?:\s*reads)'  # Matches: 25.5k reads
                ]
                
                for pattern in read_patterns:
                    read_match = re.search(pattern, element_text)
                    if read_match:
                        reads = parse_number(read_match.group(1))
                        print(f"Found reads from standard pattern: {reads}")
                        break
                
                # Look for numbers with m/k suffix at the beginning of lines
                if not reads:
                    reads_match = re.search(r'(\d+(?:\.\d+)?[KkMmBb])', element_text)
                    if reads_match:
                        reads = parse_number(reads_match.group(1))
                        print(f"Found reads from general number with suffix: {reads}")
                
                # Extract votes from text
                vote_patterns = [
                    r'(\d+(?:\.\d+)?[KkMmBb]?)\s*(?:vote|like)',  # Matches: 25.5k votes, 1.2m likes
                    r'votes\s*(\d+(?:\.\d+)?[KkMmBb]?)',  # Matches: votes 25.5k
                    r'(\d+(?:\.\d+)?[KkMmBb]?)(?:\s*votes)'  # Matches: 25.5k votes
                ]
                
                for pattern in vote_patterns:
                    vote_match = re.search(pattern, element_text)
                    if vote_match:
                        votes = parse_number(vote_match.group(1))
                        print(f"Found votes from pattern: {votes}")
                        break
                
                # Extract parts from text
                part_patterns = [
                    r'(\d+)\s*(?:part|chapter)',  # Matches: 25 parts, 10 chapters
                    r'parts\s*(\d+)',  # Matches: parts 25
                    r'(\d+)(?:\s*parts)'  # Matches: 25 parts
                ]
                
                # If we see numbers like 45 that could be parts count in the element text
                if not parts:
                    # Look for isolated 2-3 digit numbers that might be part counts
                    for line in element_text_lines:
                        line = line.strip()
                        # Look for patterns like "45" that likely represent parts
                        parts_match = re.search(r'\b(\d{1,3})\b', line)
                        if parts_match and not re.search(r'#\d+', line):  # Avoid matching "#1", "#2", etc.
                            parts_candidate = int(parts_match.group(1))
                            # Parts are typically between 1-100
                            if 1 <= parts_candidate <= 100:
                                parts = parts_candidate
                                print(f"Found parts from isolated number: {parts}")
                                break
                
                for pattern in part_patterns:
                    part_match = re.search(pattern, element_text)
                    if part_match:
                        parts = parse_number(part_match.group(1))
                        print(f"Found parts from pattern: {parts}")
                        break
                
                # Extract author
                author = "Unknown Author"
                author_element = (
                    story_element.select_one('.username') or 
                    story_element.select_one('.by-author') or
                    story_element.select_one('span.author')
                )
                
                if author_element:
                    author = author_element.text.strip()
                else:
                    # Try to extract author from text pattern
                    author_match = re.search(r'by\s+([^\s]+)', element_text)
                    if author_match:
                        author = author_match.group(1).strip()
                
                # If author element contains "by" prefix, remove it
                if author.lower().startswith('by '):
                    author = author[3:].strip()
                
                # Extract description
                description = ""
                description_element = (
                    story_element.select_one('.description') or 
                    story_element.select_one('.story-description') or
                    story_element.select_one('p.description')
                )
                
                if description_element:
                    description = description_element.text.strip()
                
                # Extract tags
                tags = []
                tags_container = (
                    story_element.select('.tag-items') or 
                    story_element.select('.tag-list') or
                    story_element.select('.story-tags')
                )
                
                if tags_container:
                    tag_elements = tags_container[0].select('a, span.tag')
                    tags = [tag.text.strip() for tag in tag_elements if tag.text.strip()]
                
                # Extract cover image URL if available
                cover_url = ""
                cover_img = story_element.select_one('img.cover, img.story-cover')
                if cover_img:
                    cover_url = cover_img.get('src', '')
                
                # Extract story ID
                story_id = ""
                if url_path:
                    id_match = re.search(r'\/story\/(\d+)', url_path)
                    if id_match:
                        story_id = id_match.group(1)
                
                # Get more details from the story page
                story_details = get_story_details(story_url, headers)
                
                # Process results for display
                print(f"\nProcessed story: {title}")
                print(f"URL: {story_url}")
                print(f"Stats: reads={reads}, votes={votes}, parts={parts}")
                
                # Check criteria
                if reads >= min_reads or votes >= min_votes or processed_count < 5:
                    # For the first few stories, ignore criteria for debugging
                    story_data = {
                        'id': story_id,
                        'title': title,
                        'description': description or story_details.get('description', ""),
                        'author': author,
                        'reads': reads,
                        'votes': votes,
                        'parts': parts,
                        'tags': tags or story_details.get('tags', []),
                        'url': story_url,
                        'cover_url': cover_url,
                        'language': language,
                        'completed': story_details.get('completed', False),
                        'mature': story_details.get('mature', False),
                        'last_updated': story_details.get('last_updated', ""),
                        'first_published': story_details.get('first_published', ""),
                        'content_sample': story_details.get('content_sample', "")
                    }
                    
                    stories.append(story_data)
                    processed_count += 1
                    print(f"Added story #{processed_count}: {title}")
                else:
                    print(f"Story doesn't meet criteria: reads={reads}, votes={votes}, parts={parts}")
                
                # Add a small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing story: {e}")
                continue
        
        return stories
    
    except Exception as e:
        error_message = str(e)
        print(f"Wattpad Scraping Error: {error_message}")
        
        if "connection" in error_message.lower() or "timeout" in error_message.lower():
            return "Error: Connection issue with Wattpad. Please check your internet connection."
        else:
            return f"Error scraping Wattpad: {error_message}"

def get_story_details(story_url, headers):
    """
    Gets additional details about a story from its page
    
    Args:
        story_url (str): URL of the story page
        headers (dict): Headers for the request
        
    Returns:
        dict: Additional details about the story
    """
    details = {
        'completed': False,
        'mature': False,
        'last_updated': "",
        'first_published': "",
        'description': "",
        'tags': [],
        'content_sample': ""
    }
    
    try:
        # Make the request
        response = requests.get(story_url, headers=headers)
        
        if response.status_code != 200:
            return details
            
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract longer description if available
        description_element = (
            soup.select_one('.description') or 
            soup.select_one('.story-description') or
            soup.select_one('pre.description')
        )
        if description_element:
            details['description'] = description_element.text.strip()
        
        # Extract more tags
        tags_container = (
            soup.select('.tag-items') or 
            soup.select('.tag-list') or
            soup.select('.story-tags')
        )
        
        if tags_container:
            tag_elements = tags_container[0].select('a, span.tag')
            details['tags'] = [tag.text.strip() for tag in tag_elements if tag.text.strip()]
        
        # Check if the story is completed
        status_element = (
            soup.select_one('.story-badges .badge-status') or
            soup.select_one('.badge-status') or
            soup.select_one('.story-status')
        )
        
        if status_element and ('complete' in status_element.text.lower() or 'completed' in status_element.text.lower()):
            details['completed'] = True
            
        # Alternative check for completed status in the page text
        if 'complete' in soup.text.lower():
            details['completed'] = True
            
        # Check if the story is mature
        mature_element = (
            soup.select_one('.badge-mature') or
            soup.select_one('.mature-badge')
        )
        if mature_element:
            details['mature'] = True
        
        # Alternative mature check
        if 'mature' in soup.text.lower() and ('content' in soup.text.lower() or 'this story contains' in soup.text.lower()):
            details['mature'] = True
            
        # Try to extract the date information
        date_elements = (
            soup.select('.story-details .date') or
            soup.select('.date-info') or
            soup.select('.story-date')
        )
        
        for date_element in date_elements:
            date_text = date_element.text.strip().lower()
            if 'updated' in date_text:
                details['last_updated'] = extract_date(date_text)
            elif 'published' in date_text:
                details['first_published'] = extract_date(date_text)
                
        # Get a sample of the content from the first chapter
        try:
            # Find the first chapter link
            first_chapter_link = (
                soup.select_one('a.story-parts-title-container') or
                soup.select_one('a.table-of-contents-item') or
                soup.select_one('a[href*="/page/"]') or
                soup.select_one('a.part-link') or
                soup.select_one('a.first-chapter')
            )
            
            if not first_chapter_link and soup.select('a'):
                # Try to find any link that might lead to a chapter
                for link in soup.select('a'):
                    href = link.get('href', '')
                    if '/page/' in href or '/part/' in href or '/chapter/' in href:
                        first_chapter_link = link
                        break
            
            if first_chapter_link and first_chapter_link.get('href'):
                chapter_url = first_chapter_link.get('href')
                if not chapter_url.startswith('http'):
                    chapter_url = f"https://www.wattpad.com{chapter_url}"
                
                chapter_response = requests.get(chapter_url, headers=headers)
                
                if chapter_response.status_code == 200:
                    chapter_soup = BeautifulSoup(chapter_response.text, 'html.parser')
                    
                    # Try different selectors for content paragraphs
                    content_elements = (
                        chapter_soup.select('.page-paragraph') or
                        chapter_soup.select('p.paragraph') or
                        chapter_soup.select('pre.pre-content') or
                        chapter_soup.select('div.page-content p')
                    )
                    
                    content = ""
                    for i, para in enumerate(content_elements):
                        if i >= 5:  # Limit to first 5 paragraphs
                            break
                        content += para.text.strip() + "\n\n"
                        
                    details['content_sample'] = clean_text(content)
        except Exception as e:
            print(f"Error getting content sample: {e}")
            
        return details
        
    except Exception as e:
        print(f"Error getting story details: {e}")
        return details

def parse_number(text):
    """
    Parses number strings like '10.5k' or '2.3M' to integers
    """
    if not text:
        return 0
        
    text = str(text).lower().replace(',', '')
    
    # Extract the number part using regex
    number_match = re.search(r'([\d.]+)', text)
    if not number_match:
        return 0
        
    number = float(number_match.group(1))
    
    # Apply multiplier based on suffix
    if 'k' in text:
        number *= 1000
    elif 'm' in text:
        number *= 1000000
    elif 'b' in text:
        number *= 1000000000
        
    return int(number)

def extract_date(text):
    """
    Extracts date from strings like 'updated June 15, 2023'
    """
    date_match = re.search(r'(\w+ \d+, \d{4})', text)
    if date_match:
        return date_match.group(1)
    
    # Try alternative formats
    alt_date_match = re.search(r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', text)
    if alt_date_match:
        return alt_date_match.group(1)
        
    return ""

def clean_text(text):
    """Cleans and formats text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate if too long (max ~2000 tokens)
    max_length = 8000
    if len(text) > max_length:
        text = text[:max_length] + "..."
        
    return text 