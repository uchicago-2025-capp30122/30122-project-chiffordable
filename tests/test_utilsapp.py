import pandas as pd
from app.Utils_app import gdf_to_geojson, get_community_from_point, calculate_rent, get_community_from_name, get_livability_scores
from shapely import wkt
import geopandas as gpd

df_communities_test = pd.read_csv("extracted_data/cmap.csv") # Importing external data
df_communities_test = df_communities_test[["GEOG", "comm_poly"]]
df_communities_test['geometry'] = df_communities_test['comm_poly'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else x)
df_communities_test = gpd.GeoDataFrame(df_communities_test, geometry='geometry')

def test_community_point_normalset():
    coords = [(str(41.883717), str(-87.62866)),
          (str(41.71056), str(-87.53684)),
          (str(41.886917), str(-87.615364)),
          (str(41.918922), str(-87.718216)),
          (str(41.774254), str(-87.60619))]
    communities_correct = ["The Loop", "East Side", "The Loop", 
                           "Logan Square", "Woodlawn"]
    
    communities = []
    for pair in coords:
        latitude = pair[0]
        longitude = pair[1]
        community = get_community_from_point(df_communities_test, latitude, longitude)["GEOG"]
        communities.append(community)

    assert communities == communities_correct

def test_community_point_outside():
    coords = [(str(21.870553844846082), str(-102.29575199109235))]
    communities_correct = [None]
    
    communities = []
    for pair in coords:
        latitude = pair[0]
        longitude = pair[1]
        community = get_community_from_point(df_communities_test, latitude, longitude)
        if community:
            community_name = community["GEOG"]
        else:
            community_name = None
        communities.append(community_name)

    assert communities == communities_correct