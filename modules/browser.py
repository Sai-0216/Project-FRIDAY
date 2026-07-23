import webbrowser
from urllib.parse import quote
from patterns import patterns



class Browser:

    def __init__(self):
        self.websites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://github.com",
            "chatgpt": "https://chat.openai.com",
            "gmail": "https://mail.google.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "amazon": "https://www.amazon.in",
            "flipkart": "https://www.flipkart.com",
        }
    def google_search(self, query):

        webbrowser.open(
            f"https://www.google.com/search?q={quote(query)}"
        )

        return f"Searching Google for {query}"

        return True
    def youtube_search(self, query):

        webbrowser.open(
            f"https://www.youtube.com/results?search_query={quote(query)}"
        )

        return f"Playing {query} on YouTube"
    
    def open_website(self, name):

        name = name.lower().strip()

        if name in self.websites:
            webbrowser.open(self.websites[name])
            return True

        return False

        
browser = Browser()

from command_manager import manager

manager.register_prefix(
    "search ",
    browser.google_search
)

manager.register_prefix(
    "play ",
    browser.youtube_search
)