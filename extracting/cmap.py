import httpx
import csv
from pathlib import Path
from shapely.wkt import loads
from shapely import intersects, Point, contains
import pandas as pd
import dash
import dash_leaflet as dl
from shapely.geometry import Polygon, mapping
import json
import plotly.graph_objects as go
from dash import html



FINAL_CSV_PATH = Path(__file__).parent.parent / "extracted_data" / "cmap.csv" #figure this thing out ------------------
API_URL = "https://services5.arcgis.com/LcMXE3TFhi1BSaCY/arcgis/rest/services/Community_Data_Snapshots_2024/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

COMMS_TRACTS_CSV = Path(__file__).parent.parent / "extracting" / "archive" / "comms_tracts_chicago.csv"
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
            local_data["rent"]["median_rent"] = round(row_dict[head], 0)
        else:
            local_data["geo"][head] = row_dict[head]
    
    
    comm_id_features[local_data["geo"]["GEOID"]] = local_data

# creating dictionary with zip codes and the communities that are intersected with
zip_comms_features = {}

with open (COMMS_TRACTS_CSV, "r") as coms_tracts, open(ZIP_TRACTS_CSV, "r") as zips:
    comms = list(csv.DictReader(coms_tracts))
    zip_codes = list(csv.DictReader(zips))
    for zip in zip_codes:
        zip_code = int(zip["ZIP"])
        zip_poly = loads(zip["the_geom"]) #polygon of the zip code)
        zip_comms_features[zip_code] = {}

        for com in comms:
            id_community = int(com["AREA_NUMBE"])
            comm_poly = loads(com["the_geom"]) #takes a string and converts into multipolygon
            comm_id_features[id_community]["geo"]["comm_poly"] = comm_poly #adding it to the dictionary
            if zip_poly.intersects(comm_poly):
            #intersecting with zip codes
                zip_comms_features[zip_code][id_community] = comm_id_features[id_community]


# according to a Zillow listing, find the demographic characteristics of the area
def find_comm_and_zip_with_listing(lat : float , long : float, zip_code: int):
    """
    Takes the latitude, longitude and zip code and returns a dictionary with the
    demographic characteristics of the neighborhood.
    Input:
        lat: float
        long: float
        zip_code: int with 5 numbers
    Return:
        dictionary with keys geo, age, race and rent. Each value is another dictionary
    """
    listing = Point(long, lat)
    communities = zip_comms_features[zip_code]
    for comm in communities.values():
        poly = comm["geo"]["comm_poly"]
        if poly.contains(listing):
            return comm
        
# converting the data from each community to a list opf dictionaries to convert them to pandas
csv_format = []
for features in comm_id_features.values():
    flat_keys = {}
    for v in features.values():
        for k,val in v.items():
            flat_keys[k] = val
    csv_format.append(flat_keys)

# creating list with where communities only have polygons and not multypoligons
comms_with_polys = []
for com in csv_format:
    poly_geoms = list(com["comm_poly"].geoms)
    if len(poly_geoms) == 1:
        com["comm_poly"] = poly_geoms[0]
        comms_with_polys.append(com)
    else:
        for i, poly in enumerate(poly_geoms):
            new_comm = com.copy()
            new_comm["comm_poly"] = poly_geoms[i]
            comms_with_polys.append(new_comm)

print(comms_with_polys[0])
# ---------------------------------------------------------------------------------------------

import dash
import dash_leaflet as dl
import dash_html_components as html  # Ensure HTML components are imported
from dash.dependencies import Input, Output
import json
from shapely.geometry import mapping

# Convert to GeoJSON format
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": item["GEOG"]},
            "geometry": {
                "type": "Polygon",
                "coordinates": mapping(item["comm_poly"])["coordinates"]
            }
        }
        for item in comms_with_polys
    ]
}

# Dash App
app = dash.Dash(__name__)

geojson_layer = dl.GeoJSON(
    data=geojson_data,
    id="geojson-layer",
    options={"style": {"color": "blue", "weight": 2, "fillOpacity": 0.3}},
    zoomToBounds=True,
    hoverStyle={"weight": 3, "color": "red", "fillOpacity": 0.5},  # Style when hovering
    superClusterOptions={"disableClusteringAtZoom": 10},  # Ensures click detection
)

app.layout = html.Div([
    dl.Map(
        center=[41.8781, -87.6298],  # Chicago's latitude and longitude
        zoom=10,
        children=[
            dl.TileLayer(),
            geojson_layer
        ],
        style={'width': '100%', 'height': '600px'}
    ),
    html.Div(id="info-box", style={"margin-top": "10px", "fontSize": "20px"})
])

# Callback to update info when clicking on a polygon
@app.callback(
    Output("info-box", "children"),
    Input("geojson-layer", "click_feature")
)
def display_popup(feature):
    print("Feature received:", feature)  # Debugging line

    if feature is None:
        return "Click on a polygon to see details."

    properties = feature.get("properties", {})
    name = properties.get("name", "Unknown")
    return f"Clicked on: {name}"

if __name__ == '__main__':
    app.run_server(debug=True)
