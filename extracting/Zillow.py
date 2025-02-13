import time
import httpx
import lxml.html
import json
import csv
import os
import re

# ---------------------------- Utility Functions ----------------------------

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


# -------------------------- Web Scraping Functions ------------------------

def fetch_page(url: str) -> str:
    """
    Fetches the content of a webpage given a URL using httpx.
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "www.zillow.com",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
    }

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


def extract_listings(json_data: dict):
    """
    Extracts the list of property listings from the parsed JSON data.
    """
    listings = json_data['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']
    return listings

def get_listing_info(listing):
    """
    Extract data from a specific listing and returns a clean dictionary
    """
    listing_data = {}

    address = listing.get("address", "")
    detail_url = complete_link(listing.get("detailUrl", ""))
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

# ---------------------------- Pagination Function ----------------------------

def nextpage_from_xpath(response_text):
    """
    Extracts the URL for the next page using XPath.
    """
    tree = lxml.html.fromstring(response_text)
    next_page_element = tree.xpath('//a[@rel="next" and contains(@class, "PaginationButton-c11n-8-109-1__sc-1i6hxyy-0")]/@href')
    
    if next_page_element:
        next_url = complete_link(next_page_element[0])
        return next_url
    else:
        print("No more pages found.")
        return None


def paginate(url: str, max_pages: int = 20):
    """
    Paginate through multiple pages to extract listing URLs.
    """
    all_listings = []
    current_page = 1


    while url and current_page <= max_pages:
        clean_url = url.replace("chicago-il-", "")
        print(f"Fetching page {current_page}... {clean_url}")

        # Fetch the page
        html = fetch_page(clean_url)
        if not html:
            break

        # Parse the page content
        json_data = parse_script_content(html)
        if not json_data:
            break

        # Extract listings and add their URLs to the list
        listings = extract_listings(json_data)
        if not listings:
            break

        for listing in listings:
            all_listings.append(get_listing_info(listing))

        # Move to the next page
        next_url = nextpage_from_xpath(html)
        if next_url  == url:
            # We are not getting a None response for the next url never
            break

        url = next_url

        # Sleep before fetching the next page to avoid getting blocked
        time.sleep(2)
        current_page += 1

    return all_listings

# ---------------------------- CSV Output ----------------------------

def save_listings_to_csv(listings, filename="Zillow.csv", save_path="../extracted_data"):
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



# ---------------------------- Main Function ----------------------------

def main(zip_codes: list):
    """
    The main function to scrape listings from Zillow for each ZIP code.
    """
    all_results = []

    for zip_code in zip_codes:
        print(f"\nScraping ZIP Code: {zip_code}\n")
        url = f"https://www.zillow.com/{zip_code}/rentals/"
        
        listings = paginate(url)
        if listings:
            all_results.extend(listings)
            print(f"✅ {len(listings)} listings found in ZIP {zip_code}\n")
        else:
            print(f"❌ No listings found in ZIP {zip_code}\n")
                  
        # Sleep for a bit between ZIP codes to avoid getting blocked
        time.sleep(10)

    # Save all results to CSV
    save_listings_to_csv(all_results)


# ---------------------------- Example Usage ----------------------------

if __name__ == "__main__":
    zip_codes = [
    60007, 60018, 60106, #60127, 
    60131, 60601, 60602, 60603, 60604, 60605,
    60606, 60607, 60608, 60609, 60610, 60611, 60612, 60613, 60614, 60615,
    60616, 60617, 60618, 60619, 60620, 60621, 60622, 60623, 60624, 60625,
    60626, 60628, 60629, 60630, 60631, 60632, 60633, 60634, 60636, 60637,
    60638, 60639, 60640, 60641, 60642, 60643, 60644, 60645, 60646, 60647,
    60649, 60651, 60652, 60653, 60654, 60655, 60656, 60657, 60659, 60660,
    60661, 60664, 60666, 60668, 60669, 60670, 60673, 60674, 60675, 60677,
    60678, 60680, 60681, 60684, 60685, 60686, 60687, 60688, 60689, 60690,
    60691, 60693, 60694, 60695, 60696, 60697, 60699, 60701, 60706, 60707,
    60803, 60804, 60827
]

    all_data = main(zip_codes)
