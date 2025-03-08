import os
import pandas as pd
import sys
import geopandas as gpd
from shapely import wkt
import plotly.express as px

from Utils_app import calculate_rent, gdf_to_geojson, colors_communities, colors_details

# Load listings data
csv_file = os.path.join("extracted_data", "Zillow_archive.csv")
df_listings = pd.read_csv(csv_file)
df_listings["clean_price"] = pd.to_numeric(df_listings["clean_price"], errors='coerce')
df_listings["latitude"] = pd.to_numeric(df_listings["latitude"], errors='coerce')
df_listings["longitude"] = pd.to_numeric(df_listings["longitude"], errors='coerce')
df_listings['zipcode'] = df_listings['zipcode'].astype(str).str.zfill(5)

# Load communities data
sys.path.append('./extracting')
from cmap import csv_format  # Importing external data
df_communities = pd.DataFrame(csv_format)
df_communities['geometry'] = df_communities['comm_poly'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else x)
gdf_communities = gpd.GeoDataFrame(df_communities, geometry='geometry')

# Load livability index data
livability_path = os.path.join("extracted_data", "livability_incompleted.csv")
df_livability = pd.read_csv(livability_path)
df_livability['zip_code'] = df_livability['zip_code'].astype(str).str.zfill(5)

def create_combined_figure(annual_income, share_on_rent):
    max_rent = calculate_rent(annual_income, share_on_rent)
    filtered_listings = df_listings[df_listings["clean_price"] <= max_rent]
    filtered_communities = gdf_communities[gdf_communities["median_rent"] <= max_rent]
    geojson_data = gdf_to_geojson(filtered_communities)
    
    fig = px.choropleth_map(
        filtered_communities,
        geojson=geojson_data,
        locations=filtered_communities.GEOG,
        featureidkey="properties.GEOG",
        color="median_rent",
        color_continuous_scale=colors_communities,
        opacity=0.7,
        hover_name="GEOG",
        hover_data = {"GEOG":False, "median_rent":False},
        center={"lat": 41.8674, "lon": -87.6275},
        zoom=9.5,
        height=600
    )
    
    fig.add_scattermap(
        lat=filtered_listings["latitude"],
        lon=filtered_listings["longitude"],
        mode="markers",
        marker=dict(size=6, color="grey"),
        hovertext=filtered_listings.apply(lambda row: f"Price: ${row['clean_price']:,.0f}, {round(row['bedrooms'])} Bed, {round(row['bathrooms'])} Bath" 
                                   if pd.notnull(row['clean_price']) else "N/A", axis=1),
        hoverinfo="text",
        name="Listings"
    )
    
    fig.update_layout(mapbox_style="open-street-map",
                      coloraxis_colorbar=dict(title="Median rent"))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
    return fig

def age_figure(dataframe):
    figure = px.bar(dataframe, 
                  x="Age Group", 
                  y="Percentage", 
                  title="Age Distribution",
                  color="Age Group",
                  color_discrete_sequence=[colors_details[0]]*8)
    figure.update_layout(showlegend=False,
                         plot_bgcolor='white')
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(showgrid=False)
    return figure

def race_figure(dataframe):
    figure = px.bar(dataframe, 
                  x="Race", 
                  y="Percentage", 
                  title="Racial Composition",
                  color="Race",
                  color_discrete_sequence=[colors_details[1]]*8)
    figure.update_layout(showlegend=False,
                         plot_bgcolor='white')
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(showgrid=False)
    return figure

def livability_figure(dataframe):
    figure = px.bar(dataframe, 
                  x="Score", 
                  y="Category", 
                  title="Livability Scores",
                  color="Category",
                  color_discrete_sequence=[colors_details[2]]*8,
                  orientation = "h")
    figure.update_layout(showlegend=False,
                         plot_bgcolor='white')
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(showgrid=False)
    return figure

