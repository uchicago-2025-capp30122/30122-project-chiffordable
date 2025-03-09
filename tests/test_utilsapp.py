import pandas as pd
from app.Utils_app import gdf_to_geojson, get_community_from_point, calculate_rent, get_community_from_name, get_livability_scores
from shapely import wkt
import geopandas as gpd




def test_community_point():
    df_communities_test = pd.read_csv("extracted_data/cmap.csv") # Importing external data
    df_communities_test = df_communities_test[["GEOG", "comm_poly"]]
    df_communities_test['geometry'] = df_communities_test['comm_poly'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else x)
    df_communities_test = gpd.GeoDataFrame(df_communities_test, geometry='geometry')

    coords = [(str(41.883717), str(-87.62866)),
          (str(41.886776), str(-87.624725)),
          (str(41.886917), str(-87.615364)),
          (str(41.887234), str(-87.61864)),
          (str(41.8865), str(-87.61972))]
    
    communities = []
    for pair in coords:
        latitude = pair[0]
        longitude = pair[1]
        community = get_community_from_point(df_communities_test, latitude, longitude)
        print(community)
        communities.append(community)
    assert communities == []
