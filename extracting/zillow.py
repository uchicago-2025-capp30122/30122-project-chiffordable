import time
import lxml.html
import re
import httpx
from extracting.Utils import (
    complete_link,
    fetch_page,
    parse_script_content,
    save_to_csv,
    ZIP_CODES,
)
from extracting.zillow_details import get_details

BASE_URL = "https://www.zillow.com"

ZILLOW_HEADERS = {
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
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}

FILE_COLS = [
    "address",
    "detailUrl",
    "statusType",
    "zipcode",
    "latitude",
    "longitude",
    "price",
    "clean_price",
    "livingarea",
    "status",
    "listingkey",
    "bedrooms",
    "bathrooms",
]


def extract_listings(json_data: dict):
    """
    Extracts the list of property listings from the JSON data.

    """
    listings = json_data["props"]["pageProps"]["searchPageState"]["cat1"][
        "searchResults"
    ]["listResults"]
    return listings


def get_listing_info(listing) -> dict:
    """
    Extract data from a specific listing and returns a clean dictionary
    """
    listing_data = {}

    address = listing.get("address", "")
    detail_url = complete_link(BASE_URL, listing.get("detailUrl", ""))
    status_type = listing.get("statusType", "")
    lat = listing.get("latLong", {}).get("latitude", "")
    lon = listing.get("latLong", {}).get("longitude", "")
    zip_code = listing.get("addressZipcode", "")
    price = listing.get("price", None)
    livingarea = listing.get("area", None)
    status = listing.get("statusType", None)
    listingkey = listing.get("id", None)
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
        "clean_price": re.sub(r"[^\d]", "", str(price)) if price else None,
        "livingarea": livingarea,
        "status": status,
        "listingkey": listingkey,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
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


def one_zipcode_scrape(url: str, max_pages: int = 20):
    """
    Webscape and extact the information of one zip code.

    """
    all_listings = []
    fetched = set()
    current_page = 1

    # Two control methods to avoid looping in one zipcode
    # a. number of pages scraped per in the zipcode (max 20)
    # b. check that next page url is different and exists
    while url and current_page <= max_pages:
        clean_url = url.replace("chicago-il-", "")

        if url not in fetched:
            # 1. Fetch the page
            try:
                html = fetch_page(url, ZILLOW_HEADERS)
                fetched.add(url)

            except httpx.HTTPStatusError as e:
                print(f"Skipping {url} due to error: {e}")

            # 2. Parse the response
            json_data = parse_script_content(html)

            # 3. Extract listings and add their URLs to the list
            listings = extract_listings(json_data)

            for listing in listings:
                listing_info = get_listing_info(listing)

                # Case when we have a unique price in the listing
                if listing_info["price"]:
                    all_listings.append(listing_info)

                # Check if the listing needs details check
                elif not listing_info["price"] and listing_info["status"] == "FOR_RENT":
                    if listing_info["detailUrl"] not in fetched:
                        detils_info = get_details(listing_info)
                        all_listings.extend(detils_info)
                        fetched.add(listing_info["detailUrl"])

            # 4. Move to the next page
            next_url = nextpage_from_xpath(html)

            # Check that the new page is a different one
            if next_url == url:
                break

            # Update with paginated url and continue
            url = next_url
            current_page += 1

    return all_listings


# Main Function


def main(zip_codes: list):
    """
    The main function to scrape listings from Zillow for each ZIP code.
    """
    print("Starting webscraping by Zip Code, The City of Chicago has 94 Zip codes...")
    all_results = []

    for zip_code in zip_codes:
        print(f"\nScraping ZIP Code: {zip_code}...\n")
        url = f"https://www.zillow.com/{zip_code}/rentals/"

        listings = one_zipcode_scrape(url)
        if listings:
            all_results.extend(listings)
            print(f"✅ {len(listings)} listings found in ZIP {zip_code}\n")

        else:
            print(f"No listings found in ZIP {zip_code}\n")

        # Sleep for a bit between ZIP codes to avoid getting blocked
        time.sleep(2)

    # Save all results to CSV
    save_to_csv(all_results, "Zillow.csv", FILE_COLS)
    print(f"Scraping is done, we found {len(all_results)} rental places")
    print("The results were saved into Zillow.csv in the extracted data folder")
