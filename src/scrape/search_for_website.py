import requests
from requests import Response
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse
import re 
import json

from src.scrape.setup import Website, GoogleSearch


def ddg_search_website(company_name):
    query = f"{company_name} site:.se"
    encoded_query = urllib.parse.quote_plus(query)
    url = f"{Website.URL.value}?q={encoded_query}"

    try:
        response = requests.get(url, headers=Website.HEADERS.value, timeout=10)
        if response.status_code != 200:
            print("Status code:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("a.result__a")

        for link in results:
            href = link.get("href")
            if href and href.startswith("http") and all(x not in href for x in Website.WEBSITE_EXCLUSIONS.value):
                return href

        return None

    except Exception as e:
        print(f"[Error] {e}")
        return None


def brave_search_website(company_name):
    query = f"{company_name} {Website.QUERY_ADDITION.value}"
    params = {
        "q": query,
        "country": "SE",
        "search_lang": "sv",
        "ui_lang": "sv-SE",
        "count": 10
    }

    try:
        response = requests.get(Website.URL.value, headers=Website.HEADERS.value, params=params, timeout=10)
        if response.status_code != 200:
            print("Status code:", response.status_code)
        data = response.json()
        results = data.get("web", {}).get("results", [])
        for item in results:
            href = item.get("url")
            if href and all(excl not in href for excl in Website.WEBSITE_EXCLUSIONS.value):
                return href

        return None

    except Exception as e:
        print(f"[Error] {e}")
        return None
    
    
def google_search_website(company_name: str, *, num_results: int = 10, timeout: int = 10) -> str | None:
    """
    Search Google's Custom Search JSON API for the company's website (Örebro-biased)
    and return the first URL not in the exclusion list. Returns None if not found.

    Requires:
      - GOOGLE_CSE_API_KEY env var (or replace placeholder)
      - GOOGLE_CSE_CX env var (or replace placeholder)
    """
    api_key = GoogleSearch.API_KEY.value
    cx = GoogleSearch.CX.value
    query = f"{company_name}"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": max(1, min(10, num_results)),  # Google: 1..10 per call
        # Light locale biasing (keep it simple)
        "hl": "sv",        # UI language
        "lr": "lang_sv",   # restrict to Swedish
        "gl": "se",        # country bias
        "cr": "countrySE", # country restrict
    }

    try:
        print("\na")
        resp : Response = requests.get(GoogleSearch.URL.value, params=params, timeout=timeout)
        print("URL:", resp.url)
        print("Status:", resp.status_code)
        print("Content-Type:", resp.headers.get("Content-Type"))
        print("Body head:", resp.text[:300])
        if resp.status_code != 200:
            print(f"[Google CSE] Status code: {resp.status_code} - {resp.text[:200]}")
            return None

        data = json.loads(resp.text) # resp.json()
        
        items = data.get("items", []) or []

        exclusions = GoogleSearch.WEBSITE_EXCLUSIONS.value
        
        for it in items:
            href = it.get("link")
            if href and all(excl not in href for excl in exclusions):
                return href

        return None

    except requests.Timeout:
        print("[Google CSE] Request timed out.")
        return None
    except Exception as e:
        print(f"[Google CSE] Error: {e}")
        return None
    
