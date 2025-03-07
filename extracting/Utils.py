import time
import httpx
import lxml.html
import json
import csv
import os
import pandas as pd


ZIP_CODES = [
            60601, 60602, 60603, 60604, 60605, 60606, 60607, 60608, 60609,
        60610, 60611, 60612, 60613, 60614, 60615, 60616, 60617, 60618, 60619,
        60620, 60621, 60622, 60623, 60624, 60625, 60626, 60628, 60629, 60630,
        60631, 60632, 60633, 60634, 60636, 60637, 60638, 60639, 60640, 60641,
        60642, 60643, 60644, 60645, 60646, 60647, 60649, 60651, 60652, 60653,
        60654, 60655, 60656, 60657, 60659, 60660, 60661, 60666, 60668, 60669,
        60670, 60673, 60674, 60675, 60677, 60678, 60680, 60681, 60682, 60684,
        60685, 60686, 60687, 60688, 60689, 60690, 60691, 60693, 60694, 60695,
        60696, 60697, 60699, 60701, 60007, 60018, 60106, 60131, 60706, 60707, 
        60803, 60804, 60827
    ]


def complete_link(base_url, url: str) -> str:
    """
    Ensures the URL is complete. If the URL is incomplete (starts with '/'),
    it will prepend the base URL for example ('https://www.zillow.com').
    """
    if not url:
        return None

    if url.startswith(base_url):
        return url

    return base_url + url


def fetch_page(url: str, headers_input={}) -> str:
    """
    Fetches the content of a webpage given a URL using httpx.

    Returns:
        str: The response text if the request is successful.

    Raises:
        httpx.HTTPStatusError: If the response status code is not 2xx.
    """
    # print(url)
    with httpx.Client(headers=headers_input, follow_redirects=True) as client:
        response = client.get(url)

        if response.status_code != 200:  # Check if response is not OK
            raise httpx.HTTPStatusError(
                f"Error {response.status_code} in the scraping of {url}",
                request=response.request,
                response=response,
            )

        response.raise_for_status()  # This raises an HTTPStatusError if there's an issue

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


def save_to_csv(listings: list, filename, file_cols, save_path="../extracted_data"):
    """
    Saves listings to a CSV file in a specified directory.
    """
    # Ensure the directory exists
    os.makedirs(save_path, exist_ok=True)

    # Construct the full path
    full_path = os.path.join(save_path, filename)

    # Convert list of dictionaries to DataFrame to drop duplicates
    listings_df = pd.DataFrame(listings)
    listings_noduplicates = listings_df.drop_duplicates()

    # Convert back to a list of dictionaries
    listings_dict = listings_noduplicates.to_dict("records")

    with open(full_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=file_cols)
        writer.writeheader()
        writer.writerows(listings_dict)

    print(f"Data saved to {full_path}")
