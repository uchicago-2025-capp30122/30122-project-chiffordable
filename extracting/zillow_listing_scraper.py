import time
import httpx
import lxml.html
import json
import csv
import os
import re

from zillow_utils import fetch_page, parse_script_content, save_listings_to_csv


def extract_listings(json_data: dict):
    """
    Extracts the list of property listings from the parsed JSON data.
    """
    listings = json_data['props']['pageProps']['componentProps']['initialReduxState']['gdp']['building']['floorPlans']
    
    if listings is None:
        listings = json_data['props']['pageProps']['componentProps']['initialReduxState']['gdp']['building']['ungroupedUnits']
    
    return listings


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
        
        if 'price' in listing.keys():
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
    json_data = parse_script_content(html)
    if json_data:
        listings = extract_listings(json_data)
        # print("Fetching URl:", url)

    return get_listing_info(listings)


def get_missing_listings():
    with open("../extracted_data/Zillow-general.csv", "r", newline="") as f:
        data = csv.DictReader(f)

        completed_data = []
        fetched_links = set()

        for row in data:
            if not row['price']:
                url = row['detailUrl']
                if url not in fetched_links:
                    time.sleep(0.1)
                    individual_info = get_prices(url)

                    for appartment in individual_info:
                        apparment_data = {
                            "address": row['address'],
                            "detailUrl": row['detailUrl'],
                            "statusType": row['statusType'],
                            "zipcode": row['zipcode'],
                            "latitude": row['latitude'],
                            "longitude": row['longitude'],
                            "price": appartment['price'],
                            "clean_price":re.sub(r"[^\d]", "", str(appartment['price'])) if appartment['price'] else None,
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

    #return completed_data
    
    save_listings_to_csv(completed_data, "Zillow-complete.csv")