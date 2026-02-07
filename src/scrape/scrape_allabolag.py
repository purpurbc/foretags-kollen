from bs4 import BeautifulSoup
import requests
import time
import re

from src.scrape.setup import AllaBolag, SLEEP_TIME


def get_company_links(page=1):
    # Contruct the url
    url = f"{AllaBolag.SEARCH_URL.value}?location={AllaBolag.CITY.value}&sort={AllaBolag.SORT_BY.value}&revenueFrom={AllaBolag.REVENUE_LIMITS.value[0]}&revenueTo={AllaBolag.REVENUE_LIMITS.value[1]}&profitFrom={AllaBolag.PROFIT_LIMITS.value[0]}&profitTo={AllaBolag.PROFIT_LIMITS.value[1]}{f"&page={page}" if page != 1 else ""}"
    
    # Send the request
    response = requests.get(url, headers=AllaBolag.HEADERS.value)
    if response.status_code != 200:
        print(f"Fel vid hämtning av sida {page}: {response.status_code}")
        return []
    
    # Parse the msg
    soup = BeautifulSoup(response.text, "html.parser")

    # Select the "company cards" from the specified list-div
    cards = soup.select("div.SegmentationSearchResultCard-card")

    companies = []
    for card in cards:
        a_tag = card.find("a", href=True)
        if not a_tag:
            continue
        name = a_tag.text.strip()
        relative_url = a_tag["href"]
        full_url = AllaBolag.BASE_URL.value + relative_url
        companies.append({"name": name, "profile_url": full_url})
    
    return companies


def scrape_multiple_pages():
    all_companies = []
    for page in range(1, AllaBolag.NUM_PAGES.value + 1):
        print(f"* Sida {page}: ", end="")
        companies = get_company_links(page)
        if not companies:
            print("Inga fler företag hittades.")
            break
        all_companies.extend(companies)
        print(f"\tFound {len(companies)} companies, total= {len(all_companies)}")
        time.sleep(SLEEP_TIME)
    return all_companies


def extract_company_details(company):
    response = requests.get(company["profile_url"], headers=AllaBolag.HEADERS.value)
    if response.status_code != 200:
        print(f"Fel vid hämtning av företagssida: {response.status_code}")
        return company

    soup = BeautifulSoup(response.text, "html.parser")
    
    company["emails"] = []

    # --- Org-nummer from URL fallback ---
    match_org = re.search(r"/(\d{10})$", company["profile_url"])
    company["org_number"] = match_org.group(1) if match_org else None

    # --- Revenue extraction from accounting table ---
    rows = soup.select("table.AccountFiguresWidget-accountingtable tr")
    for row in rows:
        header = row.find("th")
        if header and "Omsättning" in header.text:
            td = row.find("td")
            if td:
                revenue_text = td.get_text(strip=True).replace("\xa0", "").replace(" ", "")
                try:
                    company["revenue"] = int(revenue_text)
                except ValueError:
                    company["revenue"] = None
            break

    # --- Official company info block ---
    official_info = soup.select("span.OfficialCompanyInformationCard-propertyList")
    for item in official_info:
        key = item.select_one("span.OfficialCompanyInformationCard-property")
        value = item.select_one("span.OfficialCompanyInformationCard-propertyValue")
        if not key or not value:
            continue
        k = key.text.strip().lower()
        v = value.get_text(strip=True)

        if "juridiskt namn" in k:
            company["legal_name"] = v
        elif "organisationsnummer" in k:
            company["org_number"] = v
        elif "registreringsdatum" in k:
            company["registration_date"] = v
        elif "bolagsform" in k:
            company["company_type"] = v
        elif "antal anställda" in k:
            company["employees"] = v
        elif "aktiekapital" in k:
            company["share_capital"] = v
        elif "adress" in k and "post" not in k:
            company["address"] = v
        elif "postadress" in k:
            company["postal_address"] = v
            city_match = re.search(r"\d{3}\s*\d{2}\s+(.+)", v)
            if city_match:
                company["city"] = city_match.group(1).strip()
        elif "verkställande direktör" in k:
            company["ceo"] = v

    # --- Website and email from contact info ---
    contact_blocks = soup.select("span.ContactInformationCard-smallPropertyList")
    for block in contact_blocks:
        label = block.select_one("span.ContactInformationCard-smallProperty")
        val = block.select_one("span.ContactInformationCard-smallPropertyValue")
        if not label or not val:
            continue
        label_text = label.text.strip().lower()
        value_text = val.get_text(strip=True)
        if "e-post" in label_text:
            company["emails"].append(value_text)
        elif "hemsida" in label_text:
            company["website"] = value_text

    # --- SNI codes ---
    sni_list = []
    sni_blocks = soup.select("span.OfficialCompanyInformationCard-propertyValue a[href*='naceIndustry']")
    for link in sni_blocks:
        sni_list.append(link.text.strip())
    company["sni_codes"] = sni_list
    
    # --- Contact info block (Kontaktuppgifter) ---
    contact_info_spans = soup.select("span.ContactInformationCard-smallPropertyList")
    for span in contact_info_spans:
        label = span.select_one("span.ContactInformationCard-smallProperty")
        value = span.select_one("span.ContactInformationCard-smallPropertyValue")

        if not label or not value:
            continue

        label_text = label.get_text(strip=True).lower()

        if "telefon" in label_text:
            company["phone"] = value.get_text(strip=True)
        elif "hemsida" in label_text:
            a_tag = value.find("a", href=True)
            if a_tag:
                company["website"] = a_tag["href"]
        elif "e-post" in label_text:
            btn = value.find("button")
            if btn:
                company["emails"].append(btn.get_text(strip=True))
        elif "adress" in label_text and "post" not in label_text:
            company["address"] = value.get_text(strip=True)
        elif "postadress" in label_text:
            full_address = value.get_text(strip=True)
            company["postal_address"] = full_address
            city_match = re.search(r"\d{3}\s*\d{2}\s+(.+)", full_address)
            if city_match:
                company["city"] = city_match.group(1).strip()

    # --- Verksamhet & ändamål (verksamhetsbeskrivning) ---
    desc = soup.select_one(
        "div.MuiGrid-root.MuiGrid-direction-xs-row.MuiGrid-grid-xs-12.MuiTypography-root.MuiTypography-body2.mui-18twy0e"
    )
    company["business_purpose"] = desc.get_text(" ", strip=True) if desc else None
    
    return company