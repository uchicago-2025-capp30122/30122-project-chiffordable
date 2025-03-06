import httpx
import lxml.html
import json
import csv
import os
import pandas as pd
from Utils import parse_script_content, fetch_page

INDIVIDUAL_HEADERS = {
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


def extract_listings(json_data: dict):
    """
    Extracts the list of property listings from the parsed JSON data.
    """
    try:
        partial_extract = json_data['props']['pageProps']['componentProps']['initialReduxState']['gdp']['building']
        # The details Zillow listings are under two structures and are randomply asigned 
        # 1. under the floorPlans name
        listings = partial_extract.get('floorPlans')

        # 2. under the ungroupedUnits name 
        if not listings:
            listings= partial_extract.get('ungroupedUnits')

        return listings
    
    except KeyError:
        return []


def get_listing_info(listings:list):
    """
    Extract data from a specific listing and returns a clean dictionary
    with price, number of beds, number of bathrooms, etc)
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
     """ From a detail url gets the information from each appartment
         - url: string url 

         Returns a list of  dictionaries with the 
         information of the individual listing
     """
     detail_link = str(url)
    #  try:
    #     html = fetch_page(detail_link, INDIVIDUAL_HEADERS)
    #  except httpx.HTTPStatusError as e:
    #     print(f"Skipping {url} due to error: {e}")
    #     return []  # Return an empty list or handle it as needed
     html = fetch_page(detail_link, INDIVIDUAL_HEADERS)
     if html:
        json_data = parse_script_content(html)
        if json_data:
            listings = extract_listings(json_data)
            if listings:
                return get_listing_info(listings)

     return {}
            
            
def get_details_info(listing: dict)-> list:
    """ This function takes a dictionary of a listing and returns 
        the information from sublistings.

        - listing: dictionary with general scrape from main Zillow webpage

        Returns a list of dictionaries with individual appartments information.
        The dictionaries include: address,   detailUrl,    statusType,
                                  zipcode,   latitude,     longitude,
                                  price,     clean_price,  livingarea (srft),
                                  status,    listingkey,   bedrooms, 
                                  bathrooms
    """
    
    url = listing['detailUrl']

    # Get all appartments information
    individual_info = get_prices(url)

    completed_data = []
    # Get each appartment information in the formar for the CSV 
    # and with the information from general listing (latitude, longitude, 
    # address, detail URL, zipcode, status type, listing key)
    if individual_info:
        for appartment in individual_info:
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


