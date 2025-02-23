import os
import webbrowser
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import geopandas as gpd
from shapely import wkt
import plotly.express as px
import sys  

sys.path.append('./extracting')
from cmap import csv_format  

# Load the CSV file
df = pd.DataFrame(csv_format)

# Ensure the 'comm_poly' column contains valid geometries
df['geometry'] = df['comm_poly'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else x)

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Convert GeoDataFrame to a GeoJSON dictionary
def gdf_to_geojson(gdf):
    features = []
    for _, row in gdf.iterrows():
        feature = {
            "type": "Feature",
            "geometry": row["geometry"].__geo_interface__,
            "communities": {"GEOG": row["GEOG"], "median_rent": row["median_rent"]}
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}

geojson_data = gdf_to_geojson(gdf)

# Helper function to create the map figure
def create_figure(filtered_gdf):
    geojson_filtered = gdf_to_geojson(filtered_gdf)

    fig = px.choropleth_mapbox(
        filtered_gdf,
        geojson=geojson_filtered,
        locations=filtered_gdf.index,  # Index used to match with GeoJSON
        featureidkey="communities.GEOG",  # Ensure it matches the property key in GeoJSON
        color_discrete_sequence=["lightblue"],  # Use light blue color
        hover_name="median_rent",
        hover_data=["median_rent"],
        center={"lat": 41.8781, "lon": -87.6298},  # Centered on Chicago
        zoom=10,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

default_fig = create_figure(gdf)

# Set up the Dash app layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Chicago Community Areas Map"),
    html.Div([
        html.Label("Enter maximum median rent:"),
        dcc.Input(
            id="rent-input", 
            type="number", 
            placeholder="Maximum rent", 
            value=1500  # Default value; adjust as needed
        )
    ], style={'padding': '10px', 'fontSize': '20px'}),
    dcc.Graph(id="chicago-map", figure=default_fig)
])

# Callback: update the map based on user input for maximum rent
@app.callback(
    Output("chicago-map", "figure"),
    Input("rent-input", "value")
)
def update_map(max_rent):
    if max_rent is None:
        filtered_gdf = gdf
    else:
        filtered_gdf = gdf[gdf["median_rent"] <= max_rent]
    return create_figure(filtered_gdf)

if __name__ == '__main__':
    port = 8050
    url = f"http://127.0.0.1:{port}/"
    print(f"Running on {url}")
    webbrowser.open(url, new=2)
    app.run_server(debug=True, port=port)