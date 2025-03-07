import time
import httpx
import lxml.html
import regex  as re
import csv
import os
import json

# ---------------------------- Utility Functions ----------------------------

def complete_link(zip_code: str) -> str:
    """
    Ensures the URL is complete. If the URL is incomplete (starts with '/'),
    it will prepend the base URL ('https://www.zillow.com').

    :param url: The URL to complete.
    :return: The complete URL.
    """
    base_url = "https://livabilityindex.aarp.org/search/Chicago,%20Illinois%20"
    suffix = ",%20United%20States#scores"
    return base_url + zip_code + suffix

# --------------------------- Scraper Function ------------------------------
def make_request(zip_code: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    with httpx.Client(headers = headers, follow_redirects=True) as client:
        url = complete_link(zip_code)
        response = client.get(url)
        zip_data = lxml.html.fromstring(response.text)
        print(zip_data)
        return zip_data
# --------------------------- complete link for table request--------------------------
def complete_table_scores_link(zip_code: str) -> str:
    """
    This function ensures the URL for requesting the table
    scores for a zip code is complete
    param url
    returns: a complete URL 
    """
    base_table_url = "https://api.livabilityindex.aarp.org/api/features/zip/"
    suffix_table = "/scores"

    return base_table_url + zip_code + suffix_table
# --------------------------- regex to access scores in table ---------------------
def extract_next_chars(text, categories):
   
    results = {}

    for category in categories:
        matches = re.findall(re.escape(category) + r'(.....)', text)
        if len(matches) >= 3:
            results[category] = matches[2]
            results[category] = results[category][3:]
        else: 
            results[category] = None
    return results

def make_table_request(zip_code: str):
    """
    making a request for the table scores
    """
    table_headers = {
        "Authorization": "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBQVJQLURFViIsIm5hbWUiOiJEaXJrIEhlbmlnZXMiLCJpYXQiOjE1MTYyMzkwMjJ9.YDVokWjQVnO5Oii_FWTc-uDL-ioYF9jyD9wcYfzlDjw"
    }

    with httpx.Client(headers = table_headers, follow_redirects=True) as client:
        url = complete_table_scores_link(zip_code)
        response = client.get(url)

    if response.status_code == 200:
        table_data = str(response.json())
        scores_categories = ["score_prox", "score_engage", "score_env",
                             "score_health", "score_house", "score_opp", "score_trans"]
        
        livability_scores = extract_next_chars(table_data, scores_categories)
    return livability_scores

        
# ---------------------------- Obtaining Scores by Zip_code ----------------------------
def livindex_by_zc(chicago_zip_codes: list): 

    """ 
    Extracting information by zip code for the livability index: 
    input (lst): zip_codes lists  
    output (): list of dictionaries

    """
    list_by_zip = []

    for zip_code in chicago_zip_codes:
        scores_by_zip = make_table_request(zip_code)
        scores_by_zip["zip_code"] = zip_code
        list_by_zip.append(scores_by_zip)
    
    return list_by_zip
            
    
# ---------------------------- Writing csv file----------------------------
def csv_livability(list_by_zip, filename, save_path="../extracted_data"):
    os.makedirs(save_path, exist_ok=True)
    scores_categories = ["zip_code", "score_prox", "score_engage", "score_env",
                         "score_health", "score_house", "score_opp", "score_trans"]
    full_path = os.path.join(save_path, filename)

    with open(full_path, "w", newline="") as f: 
        writer = csv.DictWriter(f, fieldnames=scores_categories)
        writer.writeheader()

        for zip_code in list_by_zip:
            row = {
                "zip_code": zip_code["zip_code"],
                "score_prox": zip_code["score_prox"],
                "score_engage": zip_code["score_engage"],
                "score_env": zip_code["score_env"], 
                "score_health": zip_code["score_health"],
                "score_house": zip_code["score_house"],
                "score_opp": zip_code["score_opp"],
                "score_trans": zip_code["score_trans"]
            }
            print(row)
            writer.writerow(row)

            
# ---------------------------- Main Function ----------------------------
def main(zip_codes: list):
    zipcodes_data = {}

    for zip_code in zip_codes:
        print(f"\n📌 Scraping ZIP Code: {zip_code}\n")
        zipcodes_data[zip_code] = make_request(zip_code)
        time.sleep(1)       
        
    return zipcodes_data

# ---------------------------- Example Usage ----------------------------

if __name__ == "__main__":
    chicago_zip_codes = [
    "60601", "60602", "60603", "60604", "60605", "60606", "60607", "60608", "60609",
    "60610", "60611", "60612", "60613", "60614", "60615", "60616", "60617", "60618", "60619",
    "60620", "60621", "60622", "60623", "60624", "60625", "60626", "60628", "60629", "60630",
    "60631", "60632", "60633", "60634", "60636", "60637", "60638", "60639", "60640", "60641",
    "60642", "60643", "60644", "60645", "60646", "60647", "60649", "60651", "60652", "60653",
    "60654", "60655", "60656", "60657", "60659", "60660", "60661", "60664", 
    "60666", "60668",
    "60669", "60670", "60673", "60674", "60675", "60677", "60678", "60680", "60681", "60682",
    "60684", "60685", "60686", "60687", "60688", "60689", "60690", "60691", "60693", "60694",
    "60695", "60696", "60697", "60699", "60701"
    ]
    chicago_zip_codes = ["60601", "60602"]
    
pass