from wattpad_scraper import fetch_wattpad_stories
import json

def test_wattpad_scraper():
    """
    Test the Wattpad scraper with a popular category and display results
    """
    print("Testing Wattpad scraper...")
    
    # Test with a popular category - 'romance'
    stories = fetch_wattpad_stories(
        category="romance",
        limit=5,
        min_reads=1000,
        min_votes=100,
        min_parts=1
    )
    
    if isinstance(stories, str):
        print(f"Error occurred: {stories}")
        return
    
    if not stories:
        print("No stories found matching criteria. Try with different parameters.")
        return
        
    print(f"Successfully fetched {len(stories)} stories!")
    
    # Display story details
    for i, story in enumerate(stories, 1):
        print(f"\nStory #{i}: {story['title']}")
        print(f"Author: {story['author']}")
        print(f"Reads: {story['reads']}, Votes: {story['votes']}, Parts: {story['parts']}")
        print(f"URL: {story['url']}")
        print(f"Description preview: {story['description'][:100]}..." if story['description'] else "No description")
        print(f"Tags: {', '.join(story['tags'])}")
        print(f"Completed: {story['completed']}, Mature: {story['mature']}")
        
    # Test with a tag search
    print("\n\nTesting tag search...")
    tag_stories = fetch_wattpad_stories(
        tag="werewolf",
        limit=3,
        min_reads=1000,
        min_votes=100,
        min_parts=1
    )
    
    if isinstance(tag_stories, str):
        print(f"Error occurred with tag search: {tag_stories}")
        return
    
    if not tag_stories:
        print("No stories found with tag search. Try with different parameters.")
        return
        
    print(f"Successfully fetched {len(tag_stories)} stories with tag search!")
    
    # Display first story details
    if tag_stories:
        story = tag_stories[0]
        print(f"\nFirst tag search result: {story['title']}")
        print(f"Author: {story['author']}")
        print(f"Reads: {story['reads']}, Votes: {story['votes']}")
        print(f"URL: {story['url']}")
        print(f"Tags: {', '.join(story['tags'])}")

if __name__ == "__main__":
    test_wattpad_scraper() 