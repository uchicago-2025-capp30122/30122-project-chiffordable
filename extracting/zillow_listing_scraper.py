import time
import httpx
import lxml.html
import json
import csv
import os
import pandas as pd
from zillow_utils import parse_script_content, save_listings_to_csv

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

    try:
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            response = client.get(url)
            
            if response.status_code == 403:
                return None  # Return None if forbidden
            
            response.raise_for_status()  # Raise an exception for other HTTP errors
            return response
    except httpx.HTTPStatusError:
        return None  # Return None if any other HTTP error occurs
    except httpx.RequestError:
        return None  # Return None if there are connection issues


def extract_listings(json_data: dict):
    """
    Extracts the list of property listings from the parsed JSON data.
    """
    try:
        partial_extract = json_data['props']['pageProps']['componentProps']['initialReduxState']['gdp']['building']
        listings = partial_extract.get('floorPlans') 
        if not listings:
            listings= partial_extract.get('ungroupedUnits')
        return listings
    except KeyError:
        return []


def get_listing_info(listings:list):
    """
    Extract data from a specific listing and returns a clean dictionary
    """

    results = []
    for listing in listings:
        listingType = listing.get('listingType')
        beds = listing.get("beds")
        baths = listing.get("baths")
        sqft = listing.get("sqft")
        min_price = listing.get("minPrice")
        max_price = listing.get("maxPrice")
        
        if listing.get("price"):
            price = listing.get('price')

            if min_price is None:
                min_price = price
            
            if max_price is None:
                max_price = price

        if listingType == 'FOR_RENT' or listingType is None:
            if min_price != max_price:
                results.append({
                    "price": max_price,
                    "beds": beds,
                    "baths": baths,
                    "sqft": sqft,
                    "type": listingType,
                })

            results.append({
                "price": min_price,
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "type": listingType,
            })
    return results



def get_prices(url)-> list:
     detail_link = str(url)
     html = fetch_page(detail_link)
     if html:
        json_data = parse_script_content(html.text)
        if json_data:
            listings = extract_listings(json_data)
            print("Fetching URl:", url)
            if listings:
                info = get_listing_info(listings)
                return info


def get_missing_listings():
    with open("../extracted_data/Zillow-general.csv", "r", newline="") as f:
        data = csv.DictReader(f)

        completed_data = []
        fetched_links = set()

        for row in data:
            if not row['price']:
                url = row['detailUrl']
                if url not in fetched_links:
                    time.sleep(0.01)
                    individual_info = get_prices(url)
                    if individual_info:
                        for appartment in individual_info:
                            apparment_data = {
                                "address": row['address'],
                                "detailUrl": row['detailUrl'],
                                "statusType": row['statusType'],
                                "zipcode": row['zipcode'],
                                "latitude": row['latitude'],
                                "longitude": row['longitude'],
                                "price": appartment['price'],
                                "clean_price": appartment['price'],
                                "livingarea": appartment['sqft'],
                                "status": row['status'],
                                "listingkey": row['listingkey'],
                                "bedrooms": appartment['beds'], 
                                "bathrooms": appartment['baths'] ,
                                }
                            
                            completed_data.append(apparment_data)

                            fetched_links.add(url)

            else:
                completed_data.append(row)
    
    # Save the cleaned data to CSV
    save_listings_to_csv(completed_data, "Zillow-complete.csv")

get_missing_listings()



