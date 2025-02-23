import httpx
import csv
from pathlib import Path
from shapely.wkt import loads
from shapely import intersects, Point, contains


FINAL_CSV_PATH = Path(__file__).parent.parent / "extracted_data" / "cmap.csv" #figure this thing out ------------------
API_URL = "https://services5.arcgis.com/LcMXE3TFhi1BSaCY/arcgis/rest/services/Community_Data_Snapshots_2024/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

COMMS_TRACTS_CSV = Path(__file__).parent.parent / "extracting" / "comms_tracts_chicago.csv"
ZIP_TRACTS_CSV = Path(__file__).parent.parent / "extracting" / "zips_tracts.csv"


def request_url_and_write_csv(url):
    """Takes the url and returns a dict with the data fetched"""
    response = httpx.get(url)
    return response.json()

# PART 1: Fetching and cleaning data from the CMAP database
#getting the headers of the csv file
raw_data =request_url_and_write_csv(API_URL)
headers = ["GEOID", "GEOG", "TOT_POP","UND5","A5_19","A20_34",
          "A35_49","A50_64","A65_74","A75_84", "OV85","WHITE","HISP","BLACK",
          "ASIAN","OTHER", "MED_RENT"]
age_headers = ["UND5","A5_19","A20_34", "A35_49","A50_64","A65_74","A75_84", "OV85"]
racial_headers = ["WHITE","HISP","BLACK", "ASIAN","OTHER"]

#getting the data from each row
comm_id_features = {}
rows = []
for row in raw_data["features"]: #all data is in the key "features"
    row_dict = row["properties"] #each row has their data in key "propoerties"
    total_pop = 0
    total_race = 0
    for age in age_headers:
        total_pop += row_dict[age]
    for race in racial_headers:
        total_race += row_dict[race]
    final_row={}
    local_data = {"geo":{}, "race": {}, "age": {}, "rent":{}}
    for head in headers:
        if head in age_headers:
            local_data["age"][head] = round(row_dict[head] / total_pop * 100, 0)
        elif head in racial_headers:
            local_data["race"][head] = round(row_dict[head] / total_race * 100, 0)
        elif head == "MED_RENT":
            local_data["rent"]["median"] = round(row_dict[head], 0)
        else:
            local_data["geo"][head] = row_dict[head]
    
    
    comm_id_features[local_data["geo"]["GEOID"]] = local_data

# adding polygon to each community

zip_comms_features = {}
#zip_codes_polys

with open (COMMS_TRACTS_CSV, "r") as coms_tracts, open(ZIP_TRACTS_CSV, "r") as zips:
    comms = list(csv.DictReader(coms_tracts))
    zip_codes = list(csv.DictReader(zips))
    for zip in zip_codes:
        zip_code = int(zip["ZIP"])
        zip_poly = loads(zip["the_geom"]) #polygon of the zip code)
        zip_comms_features[zip_code] = {}
        point = Point(-87.61116, 41.80262)
        if zip_poly.contains(point):
            print(f"zip code is {zip_code}")

        for com in comms:
            id_community = int(com["AREA_NUMBE"])
            comm_poly = loads(com["the_geom"]) #takes a string and converts into multipolygon
            comm_id_features[id_community]["geo"]["comm_poly"] = comm_poly #adding it to the dictionary
            if zip_poly.intersects(comm_poly):
            #intersecting with zip codes
                zip_comms_features[zip_code][id_community] = comm_id_features[id_community]


def find_comm_and_zip_with_listing(lat : float , long : float, zip_code: int):
    listing = Point(long, lat)
    communities = zip_comms_features[zip_code]
    for comm in communities.values():
        poly = comm["geo"]["comm_poly"]
        if poly.contains(listing):
            return comm


#print(zip_comms_features[60007])














