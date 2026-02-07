from src.scrape.scrape_allabolag import scrape_multiple_pages, extract_company_details
from src.scrape.search_for_website import google_search_website
from src.scrape.scrape_mail import find_emails_on_website
from src.scrape.setup import AllaBolag, SLEEP_TIME
from src.utils.helpers import str_to_list

import time
import csv
from pathlib import Path
import pandas as pd
import json 


fieldnames = [
    "name",
    "profile_url",
    "emails",
    "org_number",
    "revenue",
    "legal_name",
    "registration_date",
    "company_type",
    "employees",
    "ceo",
    "address",
    "postal_address",
    "city",
    "share_capital",
    "sni_codes",
    "business_purpose",
    "phone",
    "website",
]

def filename_tag():
    return f"rev-{AllaBolag.REVENUE_LIMITS.value[0]}-{AllaBolag.REVENUE_LIMITS.value[1]}_nump-{AllaBolag.NUM_PAGES.value}_sort-{AllaBolag.SORT_BY.value}"
    

def combine_csv(left_filename, right_filename, filepath : str = "data/plc/"):
    # Ensure theat the files exist
    if not Path(left_filename).exists():
        return []
        
    if not Path(right_filename).exists():
        with open(right_filename, 'w+', newline ='', encoding='utf-8') as file:    
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
    
    # Read as strings to avoid NaN/type surprises
    left  = pd.read_csv(left_filename, dtype=str)
    right = pd.read_csv(right_filename, dtype=str)

    # Normalize key (strip + lowercase); adjust if you need case-sensitive
    left["_key"]  = left["name"].fillna("").str.strip().str.lower()
    right_keys = set(right["name"].fillna("").str.strip().str.lower())

    # Keep rows whose key is NOT in right
    only_in_left = left[~left["_key"].isin(right_keys)].drop(columns="_key")
    placeholder_filename = f"{filepath}plc_{filename_tag()}.csv"
    only_in_left.to_csv(placeholder_filename, index=False)
    
    return pd.read_csv(
        placeholder_filename, 
        converters={"emails": str_to_list}).to_dict(orient="records"
    )   
        
    
if __name__ == "__main__":
    print("\n--- START SCRAPING ALLABOLAG.SE ---")
    print("====================================")
    
    # Get companies (name and profile-url)
    filepath = "data/companies/"
    companies_filename = f"{filepath}companies_{filename_tag()}.csv"
    if not Path(companies_filename).exists():
        companies = scrape_multiple_pages()
        companies_df = pd.DataFrame(companies)
        companies_df.to_csv(companies_filename, index=False)
    else:
        print(f"Already done, file exists: {companies_filename}")
        companies = pd.read_csv(companies_filename).to_dict(orient="records")
        
    print("\n--- GET COMPANY DETAILS ---")
    print("====================================")
    
    # Extract company details
    filepath = "data/details/"
    company_details_filename = f"{filepath}details_{filename_tag()}.csv"
    
    companies = combine_csv(companies_filename, company_details_filename)
    
    company_details = []
    if len(companies) > 0:
        with open(company_details_filename, 'w+', newline ='', encoding='utf-8') as file:    
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
            
            for company in companies:
                print("|",end="")
                details = extract_company_details(company)
                company_details.append(details)
                time.sleep(SLEEP_TIME)
                writer.writerow(details)
                
        company_details_df = pd.DataFrame(company_details)
        company_details_df["emails"] = company_details_df["emails"].apply(json.dumps)
        company_details_df.to_csv(company_details_filename, index=False)
    else:
        print(f"Already done, file exists: {company_details_filename}")
        company_details = pd.read_csv(company_details_filename, converters={"emails": str_to_list}).to_dict(orient="records")   

    """ print("\n\n--- FIND COMPANY WEBSITE AND EMAILS ---")
    print("====================================")
    
    # Find company website and emails
    # ========================================
    filepath = "data/web/"
    company_web_emails_filename = f"{filepath}web-emails_{filename_tag()}.csv" 
    
    company_details_full = combine_csv(company_details_filename, company_web_emails_filename)
       
    if len(company_details_full) > 0:
        with open(company_web_emails_filename, 'w+', newline ='', encoding='utf-8') as file:    
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
            
            for i, cd in enumerate(company_details_full):
                found_a_website = False
                if not isinstance(cd["website"], str):   
                    cd["website"] = google_search_website(cd["name"])
                    if cd["website"] is not None:
                        found_a_website = True
                new_emails = find_emails_on_website(cd["website"])
                cd["emails"] = cd["emails"] + new_emails if new_emails is not None else cd["emails"]
                if found_a_website:
                    print(f"* Company {i+1}:\t{cd["name"]}, num_emails= {new_emails}, found_a_website= {found_a_website}")
                
                # print(f"* Company {i+1}:\t{cd["name"]}, num_emails= {len(cd["emails"])}, website= {cd["website"]}")
                #time.sleep(SLEEP_TIME)
                writer.writerow(cd)
    else:
        print(f"Already done, file exists: {company_web_emails_filename}")
        company_details_list = pd.read_csv(company_web_emails_filename).to_dict(orient="records")    """
        
    """ # Decide CSV column order
    fields = [
        "date_written",
        "org_number", "name", "legal_name", "company_type", "registration_date",
        "employees", "share_capital", "revenue", "address", "postal_address",
        "city", "phone", "website", "profile_url", "emails", "sni_codes", "business_purpose"
    ]
    
    print("\n--- SAVE COMPANY DATA TO CSV ---")
    print("====================================")

    # Save data to csv
    # ========================================
    with open("companies.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for company in company_details_list:
            print("|",end="")
            row = {field: company.get(field, "") for field in fields}
            # Join lists into comma-separated strings
            if isinstance(row["emails"], list):
                row["emails"] = ", ".join(row["emails"])
            if isinstance(row["sni_codes"], list):
                row["sni_codes"] = ", ".join(row["sni_codes"])
            row["date_written"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow(row)
            
    print("\n\n--- DONE! ---")
    print("====================================\n") """
            