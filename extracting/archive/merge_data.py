import json
import csv


def zipcode_details(zip_code: str):
    attributes = {}
    listing_gps = []
    listing_price_area = []
    with open("../extracted_data/Zillow.csv", "r", newline="") as f:
        data = csv.DictReader(f)
        for row in data:
            if row["zipcode"] == zip_code:
                listing_gps.append((row["longitude"], row["longitude"]))
                listing_price_area.append((row["clean_price"], row["livingarea"]))
    attributes["listing_coordinates"] = listing_gps
    attributes["listing_details"] = listing_price_area

    return attributes
