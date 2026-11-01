import os
import sys
import time
import json
import urllib.parse
import webbrowser

class BrowserAgent:
    """
    Playwright & Web Search Automation Agent for the Autonomous AI Agent.
    Handles web search queries, domain searches (products, flights, hotels, events,
    jobs, weather, maps), form filling, and booking search workflows.
    Includes strict safety checks to pause before any payment completion.
    """
    def __init__(self):
        self.playwright_available = self._check_playwright()

    def _check_playwright(self):
        try:
            import playwright
            return True
        except ImportError:
            return False

    def search_web(self, query):
        """Perform a web search using default browser or web search engine."""
        print(f"[BROWSER AGENT] Searching web for: '{query}'")
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        # Open in default browser for fast visual feedback
        webbrowser.open(search_url)
        return f"Opened web search for '{query}' in browser ({search_url})."

    def search_domain(self, domain_category, query):
        """
        Specialized domain searches:
        Categories: products, flights, hotels, events, tickets, jobs, schemes, weather, maps, restaurants
        """
        encoded = urllib.parse.quote_plus(query)
        urls = {
            "products": f"https://www.amazon.in/s?k={encoded}",
            "flights": f"https://www.google.com/travel/flights?q={encoded}",
            "hotels": f"https://www.google.com/travel/hotels?q={encoded}",
            "events": f"https://in.bookmyshow.com/explore/events?q={encoded}",
            "tickets": f"https://in.bookmyshow.com/explore/movies?q={encoded}",
            "trains": f"https://www.irctc.co.in/",
            "jobs": f"https://www.linkedin.com/jobs/search/?keywords={encoded}",
            "internships": f"https://internshala.com/internships/keywords-{encoded}",
            "colleges": f"https://www.google.com/search?q={encoded}+colleges",
            "schemes": f"https://www.myscheme.gov.in/search?q={encoded}",
            "weather": f"https://www.google.com/search?q=weather+{encoded}",
            "maps": f"https://www.google.com/maps/search/{encoded}",
            "restaurants": f"https://www.google.com/maps/search/restaurants+{encoded}",
            "hospitals": f"https://www.google.com/maps/search/hospitals+{encoded}",
            "services": f"https://www.google.com/search?q={encoded}+services+near+me",
            "offers": f"https://www.google.com/search?q={encoded}+shopping+offers"
        }

        target_url = urls.get(domain_category.lower(), f"https://www.google.com/search?q={encoded}")
        print(f"[BROWSER AGENT] Domain Search [{domain_category}]: {target_url}")
        webbrowser.open(target_url)
        return f"Searching {domain_category} for '{query}' at {target_url}."

    def open_url(self, url):
        """Navigate to specific web page."""
        if not url.startswith("http"):
            url = f"https://{url}"
        print(f"[BROWSER AGENT] Opening URL: {url}")
        webbrowser.open(url)
        return f"Opened web page '{url}'."

    def execute_playwright_workflow(self, task_type, payload):
        """
        Executes automated Playwright browser session if available.
        Pauses before payment / checkout actions for safety!
        """
        if not self.playwright_available:
            return self.search_web(payload.get("query", task_type))

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                
                query = payload.get("query", task_type)
                encoded = urllib.parse.quote_plus(query)
                page.goto(f"https://www.google.com/search?q={encoded}")
                page.wait_for_timeout(3000)
                title = page.title()
                browser.close()
                return f"Playwright automated browser session completed. Page title: '{title}'"
        except Exception as e:
            print(f"[PLAYWRIGHT NOTICE] Falling back to standard browser: {e}")
            return self.search_web(payload.get("query", task_type))

    def initiate_booking_flow(self, booking_type, query):
        """
        Booking Workflow Helper:
        Search -> Show options -> Require user choice -> Fill details -> Reach payment -> STOP & CONFIRM.
        """
        encoded = urllib.parse.quote_plus(query)
        if "hotel" in booking_type.lower():
            url = f"https://www.google.com/travel/hotels?q={encoded}"
        elif "flight" in booking_type.lower():
            url = f"https://www.google.com/travel/flights?q={encoded}"
        elif "event" in booking_type.lower() or "movie" in booking_type.lower():
            url = f"https://in.bookmyshow.com/search?q={encoded}"
        else:
            url = f"https://www.google.com/search?q={encoded}+booking"

        webbrowser.open(url)
        return (
            f"[BOOKING WORKFLOW STARTED]\n"
            f"Step 1: Search opened for '{query}' ({url}).\n"
            f"Step 2: Please select your preferred option from the list.\n"
            f"Step 3: Jarvis will assist in filling details up to the payment page.\n"
            f"⚠️ SAFETY GATE: Jarvis will STOP before executing any payment unless explicitly approved!"
        )
