import pytest
from extracting.zillow_details import extract_details, get_details_info, combine_details

# Sample JSON data for normal case (floorPlans present)
SAMPLE_JSON_WITH_FLOORPLANS = {
    "props": {
        "pageProps": {
            "componentProps": {
                "initialReduxState": {
                    "gdp": {
                        "building": {
                            "floorPlans": [
                                {
                                    "listingType": "FOR_RENT",
                                    "beds": 2,
                                    "baths": 1,
                                    "sqft": 800,
                                    "minPrice": 1200,
                                    "maxPrice": 1400,
                                },
                                {
                                    "listingType": "FOR_RENT",
                                    "beds": 1,
                                    "baths": 1,
                                    "sqft": 600,
                                    "price": 1000,
                                },
                            ]
                        }
                    }
                }
            }
        }
    }
}

# Sample JSON data with ungroupedUnits instead of floorPlans
SAMPLE_JSON_WITH_UNGROUPED_UNITS = {
    "props": {
        "pageProps": {
            "componentProps": {
                "initialReduxState": {
                    "gdp": {
                        "building": {
                            "ungroupedUnits": [
                                {
                                    "listingType": "FOR_RENT",
                                    "beds": 3,
                                    "baths": 2,
                                    "sqft": 900,
                                    "minPrice": 1300,
                                    "maxPrice": 1500,
                                },
                                {
                                    "listingType": "FOR_RENT",
                                    "beds": 2,
                                    "baths": 1,
                                    "sqft": 700,
                                    "price": 1100,
                                },
                            ]
                        }
                    }
                }
            }
        }
    }
}

# Sample JSON data missing both structures (should return empty list)
SAMPLE_JSON_WITHOUT_LISTINGS = {
    "props": {
        "pageProps": {
            "componentProps": {"initialReduxState": {"gdp": {"building": {}}}}
        }
    }
}

# Completely invalid JSON structure (should return empty list)
SAMPLE_JSON_INVALID = {}

# JSON where the 'gdp' key is missing (should return empty list)
SAMPLE_JSON_MISSING_GDP = {
    "props": {"pageProps": {"componentProps": {"initialReduxState": {}}}}
}

SAMPLE_LISTINGS = [
    {
        "listingType": "FOR_RENT",
        "beds": 3,
        "baths": 2,
        "sqft": 900,
        "minPrice": 1300,
        "maxPrice": 1500,
    },
    {"listingType": "FOR_RENT", "beds": 2, "baths": 1, "sqft": 700, "price": 1100},
]

SINGLE_LISTING = [
    {"listingType": "FOR_RENT", "beds": 1, "baths": 1, "sqft": 500, "price": 800}
]

LISTING_WITHOUT_PRICE = [
    {"listingType": "FOR_RENT", "beds": 2, "baths": 1, "sqft": 600}
]

LISTING_WITH_EQUAL_MIN_MAX_PRICE = [
    {
        "listingType": "FOR_RENT",
        "beds": 3,
        "baths": 2,
        "sqft": 900,
        "minPrice": 1200,
        "maxPrice": 1200,
    }
]

SAMPLE_GENERAL = {
    "address": "123 Main St",
    "detailUrl": "https://www.zillow.com/homedetails/123-Main-St/",
    "statusType": "For Rent",
    "zipcode": "60601",
    "latitude": 41.0,
    "longitude": -87.0,
    "status": "For Rent",
    "listingkey": "12345",
}

SAMPLE_DETAILS = [
    {"price": 1400, "beds": 3, "baths": 2, "sqft": 900},
    {"price": 1200, "beds": 2, "baths": 1, "sqft": 750},
]

SAMPLE_DETAILS_SINGLE = [{"price": 1000, "beds": 1, "baths": 1, "sqft": 600}]


def test_extract_details_with_floorplans():
    """
    we want it to return 2 listings
    """
    listings = extract_details(SAMPLE_JSON_WITH_FLOORPLANS)
    assert isinstance(listings, list)
    assert len(listings) == 2
    assert listings[0]["beds"] == 2
    assert listings[1]["sqft"] == 600


def test_extract_details_with_ungrouped_units():
    """
    we want it to return 2 listings
    """
    listings = extract_details(SAMPLE_JSON_WITH_UNGROUPED_UNITS)
    assert isinstance(listings, list)
    assert len(listings) == 2
    assert listings[0]["beds"] == 3
    assert listings[1]["sqft"] == 700


def test_extract_details_without_listings():
    """We should return a None"""
    listings = extract_details(SAMPLE_JSON_WITHOUT_LISTINGS)
    assert listings == None


def test_extract_details_invalid_json():
    listings = extract_details(SAMPLE_JSON_INVALID)
    assert listings == []


def test_extract_details_missing_gdp():
    """
    One key missing in the result
    """
    listings = extract_details(SAMPLE_JSON_MISSING_GDP)
    assert listings == []


def test_get_details_info_multiple_prices():
    """Multiple price ranges, having different appartments"""
    listing_info = get_details_info(SAMPLE_LISTINGS)
    assert len(listing_info) == 3
    assert listing_info[0]["price"] == 1500
    assert listing_info[1]["price"] == 1300
    assert listing_info[2]["price"] == 1100


def test_get_details_info_single_price():
    """sinle listing test"""
    result = get_details_info(SINGLE_LISTING)
    assert len(result) == 1
    assert result[0]["price"] == 800


def test_get_details_info_missing_prices():
    """Missing price fields (empty list)"""
    result = get_details_info(LISTING_WITHOUT_PRICE)
    assert result == []


def test_get_details_info_same_min_max():
    """minPrice == maxPrice
    Do not repeat listings
    """
    result = get_details_info(LISTING_WITH_EQUAL_MIN_MAX_PRICE)
    assert len(result) == 1
    assert result[0]["price"] == 1200


def test_combine_details_multiple():
    """multiple appartments"""
    result = combine_details(SAMPLE_GENERAL, SAMPLE_DETAILS)

    assert len(result) == 2, f"Expected 2 listings but got {len(result)}"

    assert result[0]["address"] == "123 Main St"
    assert result[0]["price"] == 1400
    assert result[0]["bedrooms"] == 3

    assert result[1]["price"] == 1200
    assert result[1]["bathrooms"] == 1


def test_combine_details_single():
    """single appartments"""
    result = combine_details(SAMPLE_GENERAL, SAMPLE_DETAILS_SINGLE)

    assert len(result) == 1
    assert result[0]["price"] == 1000
    assert result[0]["bedrooms"] == 1
