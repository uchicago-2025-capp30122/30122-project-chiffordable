import httpx
import csv


URL = "https://services5.arcgis.com/LcMXE3TFhi1BSaCY/arcgis/rest/services/Community_Data_Snapshots_2024/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

def request_url_and_write_csv(url):
    """Takes the url and returns a dict with the data fetched"""
    response = httpx.get(url)
    return response.json()

#getting the headers of the csv file
raw_data =request_url_and_write_csv(URL)
headers = ["OBJECTID", "GEOID", "GEOG", "TOT_POP","UND5","A5_19","A20_34",
          "A35_49","A50_64","A65_74","A75_84", "OV85","WHITE","HISP","BLACK",
          "ASIAN","OTHER"]
pop_headers = ["UND5","A5_19","A20_34", "A35_49","A50_64","A65_74","A75_84"]
racial_headers = ["WHITE","HISP","BLACK", "ASIAN","OTHER"]

#getting the data from each row
rows = []
for row in raw_data["features"]:
    row_dict = row["properties"]
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

    rows.append(final_row)

# writing the csv file
with open("extracted_data/cmap.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)










