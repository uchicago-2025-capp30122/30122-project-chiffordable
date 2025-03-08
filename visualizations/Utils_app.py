from shapely.geometry import Point
import met_brewer

# ---------------------------- Color palette ----------------------------
colors_communities = met_brewer.met_brew(name="Tam", n=20, brew_type="continuous")
colors_details = met_brewer.met_brew(name="Tam", n=3, brew_type="discrete")

# ---------------------------- Utility functions ------------------------
def gdf_to_geojson(gdf):
    """
    Takes a GeoDataframe and transforms it into a geojson for choropleth map
    
    Inputs:
        - gdf: a GeoDataframe with the attributes
    Returns:
        - geojson file
    """
    features = []
    # Takes every row in the GeoDataframe and extracts its features:
    #   - geometry making sure it is ready for plot
    #   - properties: GEOG (name) and median_rent
    for _, row in gdf.iterrows():
        feature = {
            "type": "Feature",
            "geometry": row["geometry"].__geo_interface__,  
            "properties": {"GEOG": row["GEOG"], "median_rent": row["median_rent"]}
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}

def get_community_from_point(gdf_dataframe, lat, lon):
    """
    Obtains the community details based on latitude and longitude

    Inputs:
        - gdf_dataframe: a GeoDataframe with the community polygons
        - lat, lon: latitude and longitude of the Point selected
    Returns:
        - community: details of the community that contains the Point
    """
    # Convert lat and lon into a Point
    point = Point(lon, lat)
    for _, community in gdf_dataframe.iterrows():
        # Locate Point in community polygon
        if community.geometry.contains(point):
            return community
    return None

def get_community_from_name(gdf_dataframe, name):
    """
    Obtains the community details based on name

    Inputs:
        - gdf_dataframe: a GeoDataframe with the community polygons
        - name: name of the community
    Returns:
        - community: community details
    """
    for _, community in gdf_dataframe.iterrows():
        if community.GEOG == name:
            return community
    return None

def get_livability_scores(dataframe, zip_code):
    """
    Based on a zip code, returns the livability scores

    Inputs:
        - dataframe: livability index dataframe
        - zip_code: Zip code from listing selected
    Returns:
        - scores_data: dictionary with categories and scores
    """
    # Filter data
    scores = dataframe[dataframe['zip_code'] == zip_code]
    # Save into dictionary
    scores_data = {
        "Proximity": scores["score_prox"].values[0],
        "Engagement": scores["score_engage"].values[0],
        "Environment": scores["score_env"].values[0],
        "Health": scores["score_health"].values[0],
        "Housing": scores["score_house"].values[0],
        "Opportunity": scores["score_opp"].values[0],
        "Transportation": scores["score_trans"].values[0]
    }
    return scores_data

def calculate_rent(annual_income, share_on_rent):
    """
    Computes the maximum ammount the user is willing to spend on rent

    Inputs:
        - annual_income: The annual income of the user
        - share_on_rent: The % the user is willing to spend on rent
    Returns:
        - maximum rent
    """
    if not annual_income:
        return 0
    elif not share_on_rent:
        return annual_income
    else:
        return annual_income * share_on_rent / 100 / 12