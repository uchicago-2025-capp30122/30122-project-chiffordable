import os
import pandas as pd
import sys
import geopandas as gpd
from shapely import wkt
import plotly.express as px
from Utils_app import calculate_rent, gdf_to_geojson
from Utils_app import colors_communities, colors_details

# ---------------------------- Data wrangling ---------------------------------
# 1. Zillow listings
csv_file = os.path.join("extracted_data", "Zillow_archive.csv")
df_listings = pd.read_csv(csv_file)
# Make sure data is the correct format
df_listings["clean_price"] = pd.to_numeric(df_listings["clean_price"], errors='coerce')
df_listings["latitude"] = pd.to_numeric(df_listings["latitude"], errors='coerce')
df_listings["longitude"] = pd.to_numeric(df_listings["longitude"], errors='coerce')
df_listings['zipcode'] = df_listings['zipcode'].astype(str).str.zfill(5)

# 2. CMAP community-level data
sys.path.append('./extracting')
df_communities = pd.read_csv("extracted_data/cmap.csv") # Importing external data
# Convert each polygon into a geometric object
df_communities['geometry'] = df_communities['comm_poly'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else x)
# Transform to geopandas dataframe
gdf_communities = gpd.GeoDataFrame(df_communities, geometry='geometry')

# 3. Livability index
livability_path = os.path.join("extracted_data", "Livability.csv")
df_livability = pd.read_csv(livability_path)
# Make sure data is the correct format
df_livability['zip_code'] = df_livability['zip_code'].astype(str).str.zfill(5)

# ---------------------------- Data visualizations ----------------------------

def create_combined_figure(annual_income, share_on_rent):
    """
    MAIN VISUALIZATION:
    Prints an interactive map that shows the affordable communities and listings
    based on a maximum rent the user is willing to pay.

    Inputs:
        - annual_income (float): the annual income of the user
        - share_on_rent (float [0-100]): the share of the annual income that the 
        user is willing to spend on rent
    Returns:
        - Prints map
    """
    # Step 1: Calculate the maximum amount the user is willing to spend on rent 
    # and filter data based on threshold.
    max_rent = calculate_rent(annual_income, share_on_rent)
    filtered_listings = df_listings[df_listings["clean_price"] <= max_rent]
    filtered_communities = gdf_communities[gdf_communities["median_rent"] <= max_rent]
    geojson_data = gdf_to_geojson(filtered_communities)
    
    # Step 2: First layer of map is community-level data
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

    # Step 3: Second layer of map is listings that are affordable
    fig.add_scattermap(
        lat=filtered_listings["latitude"],
        lon=filtered_listings["longitude"],
        mode="markers",
        marker=dict(size=6, color="grey"),
        # Text to be displayed is clean price, # of bedrooms and # of bathrooms
        hovertext=filtered_listings.apply(lambda row: f"Price: ${row['clean_price']:,.0f}, {'Studio' if round(row['bedrooms']) == 0 else f'{round(row['bedrooms'])} Bed'}, {round(row['bathrooms'])} Bath" 
                        if pd.notnull(row['clean_price']) else "N/A", axis=1),
        hoverinfo="text",
        name="Listings"
    )
    # Step 4: Final layer is open street map
    fig.update_layout(mapbox_style="open-street-map",
                      coloraxis_colorbar=dict(title="Median rent"))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
    return fig

def age_figure(dataframe):
    """
    COMPLEMENTARY VISUALIZATION:
    Takes the details of a community selected or inferred from listing and
    displays a bar graph with the age distribution of the community

    Inputs:
        - dataframe: a dataframe with age group and percentage
    Returns:
        - Plot
    """
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
    """
    COMPLEMENTARY VISUALIZATION:
    Takes the details of a community selected or inferred from listing and
    displays a bar graph with the racial composition of the community

    Inputs:
        - dataframe: a dataframe with race and percentage
    Returns:
        - Plot
    """
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
    """
    COMPLEMENTARY VISUALIZATION:
    Takes the details of a zipcode inferred from listing and displays a bar 
    graph with the livability scores of the zip code
    Inputs:
        - dataframe: a dataframe with categories and scores
    Returns:
        - Plot
    """
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

