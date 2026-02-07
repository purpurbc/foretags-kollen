import re
import requests
from bs4 import BeautifulSoup
from src.scrape.setup import Mail

def find_emails_on_website(url):
    email_list = []
    for page in Mail.MAIL_SEARCH_PAGES.value:
        complete_url = f"{url}/{page}"
        try:
            resp = requests.get(complete_url, timeout=5)
            if resp.status_code != 200:
                return email_list
            
            # Extract emails
            soup = BeautifulSoup(resp.text, "html.parser")
            emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", soup.text)
            
            # Email TLD filtering
            valid_emails = []
            for e in emails:
                e = e.lower().strip()
                if any(e.endswith(tld) for tld in Mail.VALID_EMAIL_TLD.value):
                    valid_emails.append(e)
                    
            if valid_emails:
                email_list = list(set(email_list + valid_emails)) # NOTE: excludes duplicates
        except Exception as e:
            return None
    
    return email_list