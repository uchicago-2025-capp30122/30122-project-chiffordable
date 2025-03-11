import httpx
import lxml.html
import regex as re
import csv
import os
import json
from . import utils
from pathlib import Path

filename = "livability.csv"


# --------------------------- complete link for table request--------------------------
def complete_table_scores_link(zip_code: str) -> str:
    """
    This function ensures the URL for requesting the table
    scores for a zip code is complete
    param url
    imput (str): zip_code
    returns: a complete URL
    """
    base_table_url = "https://api.livabilityindex.aarp.org/api/features/zip/"
    suffix_table = "/scores"

    return base_table_url + zip_code + suffix_table


# --------------------------- regex to access scores in table ---------------------
def extract_next_chars(text, categories):
    """
    This function is a helper function to extract the scores of the table. It
    goes all over the scrapped text from the webpage request and looks
    for the scores of livability index.

    input(str): text and categories
    returns: scores for each zipcode
    """
    # Step 1: Creating an empty dictionary to store the scores for each zip code
    results = {}
    # Step 2: Extracting the score values for each categories in the table
    for category in categories:
        matches = re.findall(re.escape(category) + r"(.....)", text)
        if len(matches) >= 3:
            results[category] = matches[2]
            results[category] = results[category][3:]
        else:
            results[category] = None
    return results


def make_table_request(zip_code: str):
    """
    This function makes a request for the table scores in the AARP website
    and pull the scores by zip-code for the Chicago Area and returns one dictionary
    per zip_code that contain the Liveability Scores by category (Housing,
    Environment, Health, Transportation, Opportunity, Neighborhood).

    input (str): zip_code to obtain livability score
    output (lst): List of dictionaries with scores
    """

    table_headers = {
        "Authorization": "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBQVJQLURFViIsIm5hbWUiOiJEaXJrIEhlbmlnZXMiLCJpYXQiOjE1MTYyMzkwMjJ9.YDVokWjQVnO5Oii_FWTc-uDL-ioYF9jyD9wcYfzlDjw"
    }

    with httpx.Client(headers=table_headers, follow_redirects=True) as client:
        url = complete_table_scores_link(zip_code)
        response = client.get(url)

    if response.status_code == 200:
        table_data = str(response.json())
        scores_categories = [
            "score_prox",
            "score_engage",
            "score_env",
            "score_health",
            "score_house",
            "score_opp",
            "score_trans",
        ]

        livability_scores = extract_next_chars(table_data, scores_categories)
    return livability_scores


# ---------------------------- Obtaining Scores by Zip_code ----------------------------
def livindex_by_zc(chicago_zip_codes: list):
    """
    Extracting information by zip code for the livability index:
    input (lst): zip_codes lists
    output (): list of dictionaries

    """
    # Step 1: Creating an empty list
    list_by_zip = []

    # Step 2: Looping over the list of zipcodes in Chicago to obtain the scores
    for zip_code in chicago_zip_codes:
        # Step 3: Creating scores dictionary
        scores_by_zip = make_table_request(zip_code)
        # Step 4: Handling the cases when there is no information for a zip-code
        if scores_by_zip is None:
            list_by_zip.append({"zip_code": zip_code})
        else:
            scores_by_zip["zip_code"] = zip_code
            list_by_zip.append(scores_by_zip)

    return list_by_zip


# ---------------------------- Running function ----------------------------
# List of zip-codes from Chicago Area where information is available
chicago_zip_codes_sc = [
    "60601",
    "60602",
    "60603",
    "60604",
    "60605",
    "60606",
    "60607",
    "60608",
    "60609",
    "60610",
    "60611",
    "60612",
    "60613",
    "60614",
    "60615",
    "60616",
    "60617",
    "60618",
    "60619",
    "60620",
    "60621",
    "60622",
    "60623",
    "60624",
    "60625",
    "60626",
    "60628",
    "60629",
    "60630",
    "60631",
    "60632",
    "60633",
    "60634",
    "60636",
    "60637",
    "60638",
    "60639",
    "60640",
    "60641",
    "60642",
    "60643",
    "60644",
    "60645",
    "60646",
    "60647",
    "60649",
    "60651",
    "60652",
    "60653",
    "60654",
    "60655",
    "60656",
    "60657",
    "60659",
    "60660",
    "60661",
]
# List of scores obtained manually
zips_noscrp = [
    {
        "zip_code": "60664",
        "score_prox": "83",
        "score_engage": "57",
        "score_env": "27",
        "score_health": "66",
        "score_house": "45",
        "score_opp": "21",
        "score_trans": "87",
    },
    {
        "zip_code": "60666",
        "score_prox": "63",
        "score_engage": "43",
        "score_env": "25",
        "score_health": "57",
        "score_house": "55",
        "score_opp": "45",
        "score_trans": "53",
    },
    {
        "zip_code": "60668",
        "score_prox": "78",
        "score_engage": "58",
        "score_env": "37",
        "score_health": "48",
        "score_house": "60",
        "score_opp": "34",
        "score_trans": "76",
    },
    {
        "zip_code": "60669",
        "score_prox": "76",
        "score_engage": "56",
        "score_env": "32",
        "score_health": "52",
        "score_house": "45",
        "score_opp": "25",
        "score_trans": "82",
    },
    {
        "zip_code": "60670",
        "score_prox": "83",
        "score_engage": "57",
        "score_env": "27",
        "score_health": "66",
        "score_house": "45",
        "score_opp": "21",
        "score_trans": "87",
    },
    {
        "zip_code": "60673",
        "score_prox": "46",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "62",
        "score_house": "46",
        "score_opp": "21",
        "score_trans": "74",
    },
    {
        "zip_code": "60674",
        "score_prox": "80",
        "score_engage": "55",
        "score_env": "28",
        "score_health": "67",
        "score_house": "50",
        "score_opp": "23",
        "score_trans": "86",
    },
    {
        "zip_code": "60675",
        "score_prox": "80",
        "score_engage": "55",
        "score_env": "28",
        "score_health": "67",
        "score_house": "50",
        "score_opp": "23",
        "score_trans": "86",
    },
    {
        "zip_code": "60677",
        "score_prox": "78",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "62",
        "score_house": "46",
        "score_opp": "21",
        "score_trans": "84",
    },
    {
        "zip_code": "60678",
        "score_prox": "83",
        "score_engage": "57",
        "score_env": "27",
        "score_health": "66",
        "score_house": "45",
        "score_opp": "21",
        "score_trans": "87",
    },
    {
        "zip_code": "60680",
        "score_prox": "78",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "62",
        "score_house": "46",
        "score_opp": "21",
        "score_trans": "84",
    },
    {
        "zip_code": "60681",
        "score_prox": "76",
        "score_engage": "57",
        "score_env": "27",
        "score_health": "67",
        "score_house": "39",
        "score_opp": "29",
        "score_trans": "87",
    },
    {
        "zip_code": "60682",
        "score_prox": "76",
        "score_engage": "56",
        "score_env": "32",
        "score_health": "52",
        "score_house": "45",
        "score_opp": "25",
        "score_trans": "82",
    },
    {
        "zip_code": "60684",
        "score_prox": "78",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "62",
        "score_house": "46",
        "score_opp": "21",
        "score_trans": "84",
    },
    {
        "zip_code": "60685",
        "score_prox": "77",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "65",
        "score_house": "54",
        "score_opp": "20",
        "score_trans": "84",
    },
    {
        "zip_code": "60686",
        "score_prox": "71",
        "score_engage": "56",
        "score_env": "38",
        "score_health": "37",
        "score_house": "61",
        "score_opp": "34",
        "score_trans": "78",
    },
    {
        "zip_code": "60687",
        "score_prox": "80",
        "score_engage": "55",
        "score_env": "28",
        "score_health": "67",
        "score_house": "50",
        "score_opp": "23",
        "score_trans": "86",
    },
    {
        "zip_code": "60688",
        "score_prox": "63",
        "score_engage": "43",
        "score_env": "25",
        "score_health": "57",
        "score_house": "55",
        "score_opp": "45",
        "score_trans": "53",
    },
    {
        "zip_code": "60689",
        "score_prox": "76",
        "score_engage": "56",
        "score_env": "32",
        "score_health": "52",
        "score_house": "45",
        "score_opp": "25",
        "score_trans": "82",
    },
    {
        "zip_code": "60690",
        "score_prox": "77",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "65",
        "score_house": "54",
        "score_opp": "20",
        "score_trans": "84",
    },
    {
        "zip_code": "60691",
        "score_prox": "77",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "65",
        "score_house": "54",
        "score_opp": "20",
        "score_trans": "84",
    },
    {
        "zip_code": "60693",
        "score_prox": "77",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "65",
        "score_house": "54",
        "score_opp": "20",
        "score_trans": "84",
    },
    {
        "zip_code": "60694",
        "score_prox": "80",
        "score_engage": "55",
        "score_env": "28",
        "score_health": "67",
        "score_house": "50",
        "score_opp": "23",
        "score_trans": "86",
    },
    {
        "zip_code": "60695",
        "score_prox": "76",
        "score_engage": "56",
        "score_env": "32",
        "score_health": "52",
        "score_house": "45",
        "score_opp": "25",
        "score_trans": "82",
    },
    {
        "zip_code": "60696",
        "score_prox": "77",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "65",
        "score_house": "54",
        "score_opp": "20",
        "score_trans": "84",
    },
    {
        "zip_code": "60697",
        "score_prox": "77",
        "score_engage": "56",
        "score_env": "30",
        "score_health": "65",
        "score_house": "54",
        "score_opp": "20",
        "score_trans": "84",
    },
    {
        "zip_code": "60699",
        "score_prox": "76",
        "score_engage": "56",
        "score_env": "32",
        "score_health": "52",
        "score_house": "45",
        "score_opp": "25",
        "score_trans": "82",
    },
    {
        "zip_code": "60701",
        "score_prox": "49",
        "score_engage": "43",
        "score_env": "25",
        "score_health": "57",
        "score_house": "55",
        "score_opp": "45",
        "score_trans": "53",
    },
]


# ---------------------------- Function to wirte csv file ----------------------
def write_csv():
    # Step 1: Running the scraper for the zipcodes that contain information
    sc_indexes = livindex_by_zc(chicago_zip_codes_sc)

    # Step 2: Creating the headers for the csv file
    scores_categories = [
        "zip_code",
        "score_prox",
        "score_engage",
        "score_env",
        "score_health",
        "score_house",
        "score_opp",
        "score_trans",
    ]
    # Step 3: Merging the zip codes from the scrapper and the ones obtained manyally
    all_zip_codes_data = sc_indexes + zips_noscrp
    # Step 4: Giving a path to create the csv file
    address_csv = address_csv = (
        Path(__file__).parent.parent / "extracted_data" / "livability.csv"
    )

    with open(address_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=scores_categories)
        writer.writeheader()
        writer.writerows(all_zip_codes_data)


# ---------------------------- Writing csv file ----------------------------
write_csv()
