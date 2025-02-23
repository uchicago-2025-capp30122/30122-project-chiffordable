import time
import httpx
import lxml.html
import json
import csv
import os
import re
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

default_headers = { 
        "authority": "www.zillow.com",
        "method": "GET",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "zguid=24|%24a54d78f6-9268-4405-9be6-3f3663abd80e",  # Replace with your actual cookies if needed
        "priority": "u=0, i",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        }

def fetch_page(url: str, headers= default_headers) -> str:
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


def save_listings_to_csv(listings, filename, save_path="../extracted_data"):
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

    with open(full_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(listings)

    print(f"Data saved to {full_path}")