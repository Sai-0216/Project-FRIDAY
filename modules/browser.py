"""
Project FRIDAY
Browser Controller
"""

import os
import webbrowser

import requests

from urllib.parse import quote
from dotenv import load_dotenv


load_dotenv()


class Browser:

    def __init__(self):

        self.websites = {

            "google":
                "https://www.google.com",

            "youtube":
                "https://www.youtube.com",

            "github":
                "https://github.com",

            "chatgpt":
                "https://chat.openai.com",

            "gmail":
                "https://mail.google.com",

            "facebook":
                "https://www.facebook.com",

            "instagram":
                "https://www.instagram.com",

            "linkedin":
                "https://www.linkedin.com",

            "amazon":
                "https://www.amazon.in",

            "flipkart":
                "https://www.flipkart.com",
        }

        self.youtube_api_key = os.getenv(
            "YOUTUBE_API_KEY"
        )

    # ========================================
    # GOOGLE SEARCH
    # ========================================

    def google_search(
        self,
        query
    ):

        query = str(
            query
        ).strip()

        if not query:

            return (
                "What would you like me "
                "to search for on Google?"
            )

        webbrowser.open(
            "https://www.google.com/search?q="
            + quote(query)
        )

        return (
            f"Searching Google for {query}."
        )

    # ========================================
    # YOUTUBE SEARCH
    # ========================================

    def youtube_search(
        self,
        query
    ):

        query = str(
            query
        ).strip()

        if not query:

            return (
                "What would you like me "
                "to search for on YouTube?"
            )

        webbrowser.open(
            "https://www.youtube.com/results?search_query="
            + quote(query)
        )

        return (
            f"Searching YouTube for {query}."
        )

    # ========================================
    # YOUTUBE PLAY
    # ========================================

    def youtube_play(
        self,
        query
    ):

        query = str(
            query
        ).strip()

        if not query:

            return (
                "What would you like me "
                "to play on YouTube?"
            )

        # ----------------------------------------
        # Check API key
        # ----------------------------------------

        if not self.youtube_api_key:

            print(
                "[Browser] YOUTUBE_API_KEY "
                "is missing."
            )

            return (
                "The YouTube API key is not "
                "configured, Sir."
            )

        # ----------------------------------------
        # Search YouTube
        # ----------------------------------------

        url = (
            "https://www.googleapis.com/"
            "youtube/v3/search"
        )

        params = {

            "part": "snippet",

            "q": query,

            "type": "video",

            "maxResults": 1,

            "key": self.youtube_api_key,
        }

        try:

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as e:

            print(
                "[Browser] YouTube API error:",
                repr(e)
            )

            return (
                "Sorry Sir, I couldn't contact "
                "the YouTube service."
            )

        except ValueError as e:

            print(
                "[Browser] Invalid YouTube "
                "response:",
                repr(e)
            )

            return (
                "Sorry Sir, I received an invalid "
                "response from YouTube."
            )

        # ----------------------------------------
        # Find first video
        # ----------------------------------------

        items = data.get(
            "items",
            []
        )

        if not items:

            return (
                f"I couldn't find a YouTube "
                f"video for {query}."
            )

        video_id = (
            items[0]
            .get("id", {})
            .get("videoId")
        )

        if not video_id:

            return (
                "I found a YouTube result, "
                "but it wasn't a playable video."
            )

        # ----------------------------------------
        # Open actual video
        # ----------------------------------------

        video_url = (
            "https://www.youtube.com/watch?v="
            + quote(
                str(video_id)
            )
        )

        print(
            "[Browser] YouTube video:",
            video_url
        )

        webbrowser.open(
            video_url
        )

        return (
            f"Playing {query} on YouTube."
        )

    # ========================================
    # OPEN WEBSITE
    # ========================================

    def open_website(
        self,
        name
    ):

        name = str(
            name
        ).lower().strip()

        if name in self.websites:

            webbrowser.open(
                self.websites[name]
            )

            return (
                f"Opening {name}."
            )

        return (
            f"Sorry Sir, I don't know "
            f"the website {name}."
        )


# ========================================
# Browser Instance
# ========================================

browser = Browser()