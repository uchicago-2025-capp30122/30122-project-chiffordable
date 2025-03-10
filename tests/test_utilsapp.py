import pandas as pd
from app.Utils_app import (
    get_community_from_point,
    calculate_rent,
    get_community_from_name,
)
from shapely import wkt
import geopandas as gpd

df_communities_test = pd.read_csv("extracted_data/cmap.csv")
df_communities_test["geometry"] = df_communities_test["comm_poly"].apply(
    lambda x: wkt.loads(x) if isinstance(x, str) else x
)
df_communities_test = gpd.GeoDataFrame(df_communities_test, geometry="geometry")


def test_community_point_normalset():
    """
    Tests if known coordinate points return the correct community names."
    """
    coords = [
        (str(41.883717), str(-87.62866)),
        (str(41.71056), str(-87.53684)),
        (str(41.886917), str(-87.615364)),
        (str(41.918922), str(-87.718216)),
        (str(41.774254), str(-87.60619)),
    ]
    communities_correct = [
        "The Loop",
        "East Side",
        "The Loop",
        "Logan Square",
        "Woodlawn",
    ]

    communities = []
    for pair in coords:
        latitude = pair[0]
        longitude = pair[1]
        community = get_community_from_point(df_communities_test, 
                                             latitude, longitude)[
            "GEOG"
        ]
        communities.append(community)

    assert communities == communities_correct


def test_community_point_outside():
    """
    Tests if coordinates outside the defined communities return None.
    """
    coords = [(str(21.870553844846082), str(-102.29575199109235))]
    communities_correct = [None]

    communities = []
    for pair in coords:
        latitude = pair[0]
        longitude = pair[1]
        community = get_community_from_point(df_communities_test, 
                                             latitude, longitude)
        if community:
            community_name = community["GEOG"]
        else:
            community_name = None
        communities.append(community_name)

    assert communities == communities_correct


def test_community_name_normalset():
    """
    Tests if known community names return correct demographic details.
    """
    community_names = ["The Loop", "East Side", "Woodlawn"]
    correct_details = [
        (41671.0, 2.6, 11.5),
        (23869.723396934627, 7.0, 86.8),
        (23865.0, 4.6, 3.1),
    ]
    details = []
    for community in community_names:
        community = get_community_from_name(df_communities_test, community)
        details_community = (community["TOT_POP"], 
                             community["UND5"], 
                             community["HISP"])
        details.append(details_community)

    assert details == correct_details


def test_community_name_unknown():
    """
    Tests if an unknown community name returns None.
    """
    community_names = ["Aguascalientes"]
    correct_details = [None]
    details = []
    for community in community_names:
        community = get_community_from_name(df_communities_test, community)
        if community:
            details_community = (
                community["TOT_POP"],
                community["UND5"],
                community["HISP"],
            )
        else:
            details_community = None
        details.append(details_community)

    assert details == correct_details


def test_calculate_rent_normalset():
    """
    Tests if rent calculations return expected values for various incomes and 
    rent share percentages.
    """
    incomes = [100000, 30000, 72000]
    shares = [10, 33.3, 41]
    correct_maxrent = [
        833.3333333333334,
        2774.9999999999995,
        3416.6666666666665,
        250.0,
        832.4999999999999,
        1025.0,
        600.0,
        1998.0,
        2460.0,
    ]
    rents = []
    for income in incomes:
        for share in shares:
            rents.append(calculate_rent(income, share))
    assert rents == correct_maxrent


def test_calculate_rent_noincome():
    """
    Tests if rent calculations return zero when income is zero.
    """
    incomes = [0, 0, 0]
    shares = [10, 33.3, 41]
    correct_maxrent = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    rents = []
    for income in incomes:
        for share in shares:
            rents.append(calculate_rent(income, share))
    assert rents == correct_maxrent


def test_calculate_rent_noshare():
    """
    Tests if rent calculations return full income when no share percentage 
    is provided.
    """
    incomes = [100000, 30000, 72000]
    shares = [None]
    correct_maxrent = incomes
    rents = []
    for income in incomes:
        for share in shares:
            rents.append(calculate_rent(income, share))
    assert rents == correct_maxrent
