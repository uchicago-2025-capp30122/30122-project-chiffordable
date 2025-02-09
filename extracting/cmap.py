import httpx
import csv


URL = "https://services5.arcgis.com/LcMXE3TFhi1BSaCY/arcgis/rest/services/Community_Data_Snapshots_2024/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

def request_url_and_write_csv(url):
    """Takes the url and returns a dict with the data fetched"""
    response = httpx.get(url)
    return response.json()

#getting the headers of the csv file
raw_data =request_url_and_write_csv(URL)
headers = raw_data["features"][0]["properties"].keys()

#getting the data from each row
rows = []
for row in raw_data["features"]:
    rows.append(row["properties"])

# writing the csv file
with open("../extracted_data/cmap.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)








