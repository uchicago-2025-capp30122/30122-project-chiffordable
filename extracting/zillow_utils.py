import time
import httpx
import lxml.html
import json
import csv
import os
import pandas as pd

def complete_link(url: str) -> str:
    """
    Ensures the URL is complete. If the URL is incomplete (starts with '/'),
    it will prepend the base URL ('https://www.zillow.com').
    """
    base_url = "https://www.zillow.com"

    if not url:
        return None

    if url.startswith(base_url):
        return url
    
    return base_url + url

headers = {
    "method": "GET",
    "scheme": "https",
    "authority": "www.zillow.com",
    "path": "/apartments/elk-grove-village-il/willow-crossing-apartments/5Xt94L/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "sessionid=abc123",
    "Host": "www.zillow.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
}


def fetch_page(url: str) -> str:
    """
    Fetches the content of a webpage given a URL using httpx.
    """

    with httpx.Client(headers=headers, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    
    
def parse_script_content(html: str):
    """
    Parses the HTML content and extracts the script tag with the '__NEXT_DATA__' ID.
    Returns the JSON content inside that script tag.
    """
    root = lxml.html.fromstring(html)
    script_element = root.xpath('//script[@id="__NEXT_DATA__"]')

    if script_element:
        script_content = script_element[0].text_content()
        return json.loads(script_content)
        
    print("Script tag with id '__NEXT_DATA__' not found.")
    return {}


def save_listings_to_csv(listings:list, filename, save_path="../extracted_data"):
    """
    Saves listings to a CSV file in a specified directory.
    """
    # Ensure the directory exists
    os.makedirs(save_path, exist_ok=True)

    # Construct the full path
    full_path = os.path.join(save_path, filename)

    fieldnames = ["address", "detailUrl", "statusType", "zipcode", "latitude", 
                  "longitude", "price", "clean_price", "livingarea", "status", "listingkey",
                  "bedrooms", "bathrooms"]

    # Convert list of dictionaries to DataFrame to drop duplicates
    listings_df = pd.DataFrame(listings)
    listings_noduplicates = listings_df.drop_duplicates()
    
    # Convert back to a list of dictionaries
    listings_dict = listings_noduplicates.to_dict("records")

    with open(full_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(listings_dict)

    print(f"Data saved to {full_path}")