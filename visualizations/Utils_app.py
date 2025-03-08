from shapely.geometry import Point
import met_brewer

colors_communities = met_brewer.met_brew(name="Tam", n=20, brew_type="continuous")
colors_details = met_brewer.met_brew(name="Tam", n=3, brew_type="discrete")

def gdf_to_geojson(gdf):
    features = []
    for _, row in gdf.iterrows():
        feature = {
            "type": "Feature",
            "geometry": row["geometry"].__geo_interface__,
            "properties": {"GEOG": row["GEOG"], "median_rent": row["median_rent"]}
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}

def get_community_from_point(gdf_dataframe, lat, lon):
    point = Point(lon, lat)
    for _, community in gdf_dataframe.iterrows():
        if community.geometry.contains(point):
            return community
    return None

def get_community_from_name(gdf_dataframe, name):
    for _, community in gdf_dataframe.iterrows():
        if community.GEOG == name:
            return community
    return None

def get_livability_scores(dataframe, zip_code):
    scores = dataframe[dataframe['zip_code'] == zip_code]
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
    if not annual_income:
        return 0
    elif not share_on_rent:
        return annual_income
    else:
        return annual_income * share_on_rent / 100 / 12