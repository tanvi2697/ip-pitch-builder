def get_default_subreddits():
    """Returns a list of default subreddits that are likely to have good adaptation material"""
    return [
        "WritingPrompts",
        "TrueOffMyChest",
        "relationships",
        "LetsNotMeet",
        "tifu",
        "nosleep",
        "AmItheAsshole",
        "confession",
        "MaliciousCompliance",
        "ProRevenge",
        "raisedbynarcissists",
        "pettyrevenge",
        "TalesFromRetail",
        "entitledparents",
        "IDontWorkHereLady",
        "TwoXChromosomes",
        "UnresolvedMysteries",
        "Glitch_in_the_Matrix",
        "AskReddit",
        "LifeProTips"
    ]

def get_default_wattpad_categories():
    """Returns a list of default Wattpad categories for story discovery"""
    return [
        "romance",
        "fantasy",
        "adventure",
        "sciencefiction",
        "mystery",
        "horror",
        "thriller",
        "action",
        "humor",
        "paranormal"
    ]

def format_reddit_url(permalink):
    """Converts a Reddit permalink to a full URL"""
    if permalink.startswith('/'):
        return f"https://www.reddit.com{permalink}"
    elif permalink.startswith('http'):
        return permalink
    else:
        return f"https://www.reddit.com/{permalink}"

def format_wattpad_url(url):
    """Ensures a Wattpad URL is properly formatted"""
    if not url or not isinstance(url, str):
        return ""
        
    if url.startswith('http'):
        return url
    elif url.startswith('/'):
        return f"https://www.wattpad.com{url}"
    else:
        return f"https://www.wattpad.com/{url}"
