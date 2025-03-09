import httpx
import csv
from pathlib import Path
from shapely.wkt import loads



FINAL_CSV_PATH = Path(__file__).parent.parent / "extracted_data" / "cmap.csv"
API_URL = "https://services5.arcgis.com/LcMXE3TFhi1BSaCY/arcgis/rest/services/Community_Data_Snapshots_2024/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

COMMS_TRACTS_CSV = Path(__file__).parent.parent / "extracting" / "archive" / "comms_tracts_chicago.csv"


def request_url(url):
    """Takes the url and returns a dict with the data fetched"""
    response = httpx.get(url)
    return response.json()

# PART 1: Fetching and cleaning data from the CMAP database
#getting the headers of the csv file
raw_data = request_url(API_URL)
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
            local_data["age"][head] = round(row_dict[head] / total_pop * 100, 1)
        elif head in racial_headers:
            local_data["race"][head] = round(row_dict[head] / total_race * 100, 1)
        elif head == "MED_RENT":
            local_data["rent"]["median_rent"] = round(row_dict[head], 1)
        else:
            local_data["geo"][head] = row_dict[head]
    
    
    comm_id_features[local_data["geo"]["GEOID"]] = local_data


# creating dictionary with zip codes and the communities that are intersected with
zip_comms_features = {}
with open(COMMS_TRACTS_CSV, "r") as coms_tracts:
    comms = list(csv.DictReader(coms_tracts))
    for com in comms:
        id_community = int(com["AREA_NUMBE"])
        comm_poly = loads(com["the_geom"]) #takes a string and converts into multipolygon
        comm_id_features[id_community]["geo"]["comm_poly"] = comm_poly #adding it to the dictionary


# converting the data from each community to a list opf dictionaries to convert them to pandas
csv_format = []
for features in comm_id_features.values():
    flat_keys = {}
    for v in features.values():
        for k,val in v.items():
            flat_keys[k] = val
    csv_format.append(flat_keys)


# Writing the CSV
headers_csv = csv_format[0].keys()
with open(FINAL_CSV_PATH, "w", newline="") as cmap_data:
    writer = csv.DictWriter(cmap_data, headers_csv)
    writer.writeheader()
    writer.writerows(csv_format)
        
