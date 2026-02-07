from enum import Enum
import os 

SLEEP_TIME = 0.5

# ===============================
# ALLABOLAG SCRAPING
# ===============================
class AllaBolag(Enum):
    NUM_PAGES = 2000
    CITY = "Örebro"
    BASE_URL = "https://www.allabolag.se"
    SEARCH_URL = BASE_URL + "/segmentering"
    SORT_BY = "revenueDesc"
    PROFIT_LIMITS = [-12153147, 85733000]
    REVENUE_LIMITS = [2000, 2000000]
    HEADERS = {
        "User-Agent": "Mozilla/5.0"
    }
    
# ===============================
# FINDING WEBSITE
# ===============================
class Website(Enum):
    URL = "https://api.search.brave.com/res/v1/web/search"
    API_KEY = "BSArV_h6dUXhXZfdkkOcFpg3bCBrups" 
    QUERY_ADDITION = "Örebro"
    WEBSITE_EXCLUSIONS = [
        "allabolag.se",
        "hitta.se",
        "bolagsfakta.se",
        "ratsit.se",
        "merinfo.se",
        "eniro.se",
        "partna.se",
        "orebro.se",
        "sverigetaxi.se",
        "jaktia.se",
        "vakanser.se"
        "proff.no",
        "proff.se",
        "wikipedia.se",
        "lantmateriet.se",
        "facebook.com",
        "facebook.se",
        "tripadvisor.se"
    ]
    HEADERS = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": API_KEY,
        "User-Agent": "Mozilla/5.0",
        "X-Loc-City": "Örebro",
        "X-Loc-State": "T",  # Sweden's counties use ISO 3166-2:SE — Örebro is "SE-T"
        "X-Loc-State-Name": "Örebro",
        "X-Loc-Country": "SE",
        "X-Loc-Postal-Code": "70280",
        "X-Timezone": "Europe/Stockholm",
    }
    
class GoogleSearch(Enum):
    URL = "https://www.googleapis.com/customsearch/v1" #"https://cse.google.com/cse?cx=e021af8ccb766465f" #"https://www.googleapis.com/customsearch/v1"
    # Best practice: keep secrets in env vars
    API_KEY = "AIzaSyDfp-knD0xsmuLHMH1bqYTKnqn7i5HG3Yk" # "AIzaSyCK9oDbKkNvNkLof0ppV33quaz8tqt8lRs" # 
    CX = "e021af8ccb766465f"
    # Domains that are rarely the official website
    WEBSITE_EXCLUSIONS = [
        # Directories / company info
        "allabolag.se","hitta.se","bolagsfakta.se","ratsit.se","merinfo.se","eniro.se",
        "proff.se","proff.no","uc.se","finder.se","partna.se","kreditrapporten.se",
        # Gov / municipal
        "orebro.se","verksamt.se","bolagsverket.se",
        # Maps
        "google.com/maps","google.se/maps","bing.com/maps","apple.com/maps",
        # Social
        "facebook.com","facebook.se","instagram.com","linkedin.com","x.com","twitter.com","tiktok.com","youtube.com",
        # Reviews
        "reco.se","trustpilot.com","trustpilot.se","yelp.com",
        # Marketplaces / booking
        "bokadirekt.se","fresha.com","booksy.com","blocket.se",
        # Food / travel
        "tripadvisor.se","thefork.se","wolt.com","foodora.se",
        # Jobs
        "arbetsformedlingen.se","indeed.com","indeed.se","monster.se","careerjet.se","vakanser.se",
        # Media / news (noisy)
        "na.se","svt.se","aftonbladet.se","expressen.se",
        # Generic partner hubs frequently causing false positives
        "orebrohockey.se", 
        
        "konkurslistan.se", 
        "newsworthy.se", 
        "ledigalagenheter.org",
    ]

# ===============================
# FINDING EMAIL SCRAPING
# ===============================
# NOTE: vissa sidor går kontaktsidan inte att gissa sig till...
class Mail(Enum):   
    MAIL_SEARCH_PAGES = [ 
        "", # homepage
        "kontakt",
        "kontakta",
        "kontakta-oss",
        "om-oss",
        "about",
        "about-us",
        "contact",
        "contact-info",
        "info",
        
        "teamet", 
        "vårt-team",
        "kontakter",
        "marketing",
        "team",
    ]
    VALID_EMAIL_TLD = {".se", ".com", ".net", ".org"}