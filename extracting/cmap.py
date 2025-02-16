import httpx
import csv
from pathlib import Path


csv_path = Path(__file__).parent.parent / "extracted_data" / "cmap.csv" #figure this thing out ------------------
URL = "https://services5.arcgis.com/LcMXE3TFhi1BSaCY/arcgis/rest/services/Community_Data_Snapshots_2024/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

def request_url_and_write_csv(url):
    """Takes the url and returns a dict with the data fetched"""
    response = httpx.get(url)
    return response.json()

#getting the headers of the csv file
raw_data =request_url_and_write_csv(URL)
headers = ["GEOID", "GEOG", "TOT_POP","UND5","A5_19","A20_34",
          "A35_49","A50_64","A65_74","A75_84", "OV85","WHITE","HISP","BLACK",
          "ASIAN","OTHER", "MED_RENT"]
pop_headers = ["UND5","A5_19","A20_34", "A35_49","A50_64","A65_74","A75_84"]
racial_headers = ["WHITE","HISP","BLACK", "ASIAN","OTHER"]

#getting the data from each row
dict_with_rows = {}
rows = []
for row in raw_data["features"]: #all data is in the key "features"
    row_dict = row["properties"] #each row has their data in key "propoerties"
    total_pop = 0
    total_race = 0
    for pop in pop_headers:
        total_pop += row_dict[pop]
    for race in racial_headers:
        total_race += row_dict[race]
    final_row={}
    for head in headers:
        if head in pop_headers:
            final_row[head] = row_dict[head] / total_pop * 100        
        elif head in racial_headers:
            final_row[head] = row_dict[head] / total_race * 100
        else:
            final_row[head] = row_dict[head]
    
    dict_with_rows[final_row["GEOID"]] = final_row
    rows.append(final_row)


# writing the csv file
with open(csv_path, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)











