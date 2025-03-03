import time
import lxml.html
import re
from Utils import complete_link, fetch_page, parse_script_content, save_listings_to_csv, ZIP_CODES
from zillow_details import get_details_info

BASE_URL = "https://www.zillow.com"

ZILLOW_HEADERS = {
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

FILE_COLS = ["address", "detailUrl", "statusType", "zipcode", "latitude", 
                "longitude", "price", "clean_price", "livingarea", 
                "status", "listingkey", "bedrooms", "bathrooms"]

def extract_listings(json_data: dict):
    """
    Extracts the list of property listings from the JSON data.

    """
    listings = json_data['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']
    return listings

def get_listing_info(listing)-> dict:
    """
    Extract data from a specific listing and returns a clean dictionary
    """
    listing_data = {}

    address = listing.get("address", "")
    detail_url = complete_link(BASE_URL , listing.get("detailUrl", ""))
    status_type = listing.get("statusType", "")
    lat = listing.get("latLong", {}).get("latitude", "")
    lon = listing.get("latLong", {}).get("longitude", "")
    zip_code = listing.get("addressZipcode", "")
    price = listing.get('price', None)
    livingarea = listing.get('area', None)
    status = listing.get('statusType', None)
    listingkey = listing.get('id', None)
    bedrooms = listing.get("beds", None)  
    bathrooms = listing.get("baths", None)  

    listing_data = {
        "address": address,
        "detailUrl": detail_url,
        "statusType": status_type,
        "zipcode": zip_code,
        "latitude": lat,
        "longitude": lon,
        "price": price,
        "clean_price":re.sub(r"[^\d]", "", str(price)) if price else None,
        "livingarea": livingarea,
        "status": status,
        "listingkey": listingkey,
        "bedrooms": bedrooms, 
        "bathrooms": bathrooms  
    }

    return listing_data

def nextpage_from_xpath(response_text):
    """
    Extracts the URL for the next page using XPath.

    - response_texts: The html from the current webpage 

    Return the next page link
    (In zillow, when there are no more pages, the next page link 
    returns the current link. 
    The exception is when there is only one page, there is no next page element)
    """
    tree = lxml.html.fromstring(response_text)
    next_page_element = tree.xpath('//a[@rel="next" and @title="Next page"]/@href')
    
    if next_page_element:
        next_url = complete_link(BASE_URL, next_page_element[0])
        return next_url
    
    return None

def one_zipcode_scrape (url: str, max_pages: int = 20):
    """
    Webscape and extact the information of one zip code. 

    """
    all_listings = []
    current_page = 1

    # Two control methods to avoid looping in one zipcode
        # a. number of pages scraped per in the zipcode (max 20)
        # b. check that next page url is different and exists
    while url and current_page <= max_pages:
        clean_url = url.replace("chicago-il-", "")

        # 1. Fetch the page
        html = fetch_page(clean_url, ZILLOW_HEADERS)

        # 2. Parse the response 
        json_data = parse_script_content(html)

        # 3. Extract listings and add their URLs to the list
        listings = extract_listings(json_data)

        for listing in listings:
            listing_info = get_listing_info(listing)
            
            # Check if the listing needs details check
            if not listing_info['price']:
                detils_info = get_details_info(listing_info)
                all_listings.extend(detils_info)

            # Case when we have a unique price in the listing
            else: 
                all_listings.append(listing_info )

        # 4. Move to the next page
        next_url = nextpage_from_xpath(html)

        # Check that the new page is a different one
        if next_url  == url:
            break

        # Update with paginated url and continue
        url = next_url
        current_page += 1

    return all_listings

# ---------------------------- Main Function ----------------------------

def main(zip_codes: list):
    """
    The main function to scrape listings from Zillow for each ZIP code.
    """
    print("Starting webscraping by Zip Code, The City of Chicago has 94 Zip codes...")
    all_results = []

    for zip_code in zip_codes:
        print(f"\nScraping ZIP Code: {zip_code}\n")
        url = f"https://www.zillow.com/{zip_code}/rentals/"
        
        listings = one_zipcode_scrape(url)
        if listings:
            all_results.extend(listings)
            print(f"✅ {len(listings)} listings found in ZIP {zip_code}\n")

        else:
            print(f"No listings found in ZIP {zip_code}\n")
                  
        # Sleep for a bit between ZIP codes to avoid getting blocked
        time.sleep(0.5)

    # Save all results to CSV
    save_listings_to_csv(all_results, "Zillow.csv", FILE_COLS)
    print(f"Scraping is done, we found {len(all_results)} rental places")
    print("The results were saved into Zillow.csv in the extracted data folder")

main(ZIP_CODES)


