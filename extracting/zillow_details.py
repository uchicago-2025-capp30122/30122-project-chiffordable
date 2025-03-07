import httpx
import lxml.html
import json
import csv
import os
import pandas as pd
from extracting.Utils import parse_script_content, fetch_page

INDIVIDUAL_HEADERS = {
"authority": "www.zillow.com",
    "method": "GET",
    "path": "/60615/rentals/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "connection": "keep-alive",
    "cookie": "sessionid=abc1234",
    "pragma": "no-cache",
    "referer": "https://www.zillow.com/",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}


def extract_details(json_data: dict):
    """
    Extracts the list of property listings from the parsed JSON data.
    """
    try:
        partial_extract = json_data['props']['pageProps']['componentProps']['initialReduxState']['gdp']['building']
        # The details Zillow listings are under two structures and are randomly asigned to the listings
        # We need to check both structures and have a resilient scraper
        # 1. under the floorPlans name
        listings = partial_extract.get('floorPlans')

        # 2. under the ungroupedUnits name 
        if not listings:
            listings= partial_extract.get('ungroupedUnits')

        return listings
    
    except KeyError:
        return []


def get_details_info(listings:list):
    """
    Extract data from a specific listing and returns a clean dictionary
    with price, number of beds, number of bathrooms, etc)

    - One different entry for each "appartment" inside a building
    - listings: list of ditionaries for each individual apparment in the listing
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

        # Do not add listings without any price   
        if min_price is None and max_price is None:
            continue

        if listingType == 'FOR_RENT' or listingType is None:
            if min_price != max_price :
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

def combine_details(listing: dict, details:list) -> dict:
    """ this function combines the general listing info with the details 
        with each appartment. 

        Returns a list of dictionaries with individual appartments information.
        The dictionaries include: address,   detailUrl,    statusType,
                                  zipcode,   latitude,     longitude,
                                  price,     clean_price,  livingarea (srft),
                                  status,    listingkey,   bedrooms, 
                                  bathrooms
    """
    completed_data = []

    for appartment in details:
            apparment_data = {
                "address": listing['address'],
                "detailUrl": listing['detailUrl'],
                "statusType": listing['statusType'],
                "zipcode": listing['zipcode'],
                "latitude": listing['latitude'],
                "longitude": listing['longitude'],
                "price": appartment['price'],
                "clean_price": appartment['price'],
                "livingarea": appartment['sqft'],
                "status": listing['status'],
                "listingkey": listing['listingkey'],
                "bedrooms": appartment['beds'], 
                "bathrooms": appartment['baths'] ,
                }
            
            completed_data.append(apparment_data)

    return completed_data



def get_prices(url)-> list:
     """ From a detail url gets the information from each appartment
         - url: string url 

         Returns a list of  dictionaries with the 
         information of the individual listing
     """
     detail_link = str(url)
     try:
         html = fetch_page(detail_link, INDIVIDUAL_HEADERS)
         
     except httpx.HTTPStatusError as e:
         print(f"Skipping {url} due to error: {e}")
         return []  # Return an empty list or handle it as needed

     if html:
        json_data = parse_script_content(html)
        if json_data:
            listings = extract_details(json_data)
            if listings:
                return get_details_info(listings)

     return {}
            
            
def get_details(listing: dict)-> list:
    """ This function takes a dictionary of a listing and returns 
        the information from sublistings.

        - listing: dictionary with general scrape from main Zillow webpage
    """
    
    url = listing['detailUrl']

    # Get all appartments information
    individual_info = get_prices(url)

    # Get each appartment information in the formar for the CSV 
    # and with the information from general listing (latitude, longitude, 
    # address, detail URL, zipcode, status type, listing key)
    if individual_info:
        return combine_details (listing, individual_info)

       


