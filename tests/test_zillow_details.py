import pytest
from extracting.zillow_details import extract_details, get_details_info, get_prices, get_details_info

SAMPLE_JSON_DETAILS = {
    'props': {
        'pageProps': {
            'componentProps': {
                'initialReduxState': {
                    'gdp': {
                        'building': {
                            'floorPlans': [
                                {"listingType": "FOR_RENT", "beds": 2, "baths": 1, "sqft": 800, "minPrice": 1200, "maxPrice": 1400},
                                {"listingType": "FOR_RENT", "beds": 1, "baths": 1, "sqft": 600, "price": 1000}
                            ]
                        }
                    }
                }
            }
        }
    }
}

SAMPLE_LISTINGS = [
    {"listingType": "FOR_RENT", "beds": 3, "baths": 2, "sqft": 900, "minPrice": 1300, "maxPrice": 1500},
    {"listingType": "FOR_RENT", "beds": 2, "baths": 1, "sqft": 700, "price": 1100},
]

SAMPLE_LISTING_DICT = {
    "address": "123 Main St",
    "detailUrl": "https://www.zillow.com/homedetails/123-Main-St/",
    "statusType": "For Rent",
    "zipcode": "60601",
    "latitude": 41.0,
    "longitude": -87.0,
    "status": "For Rent",
    "listingkey": "12345"
}

# Test extract_listings
def test_extract_listings():
    listings = extract_details(SAMPLE_JSON_DETAILS)
    assert isinstance(listings, list)
    assert len(listings) == 2
    assert listings[0]["beds"] == 2
    assert listings[1]["sqft"] == 600

def test_extract_listings_no_floorplans():
    json_without_floorplans = {
        'props': {'pageProps': {'componentProps': {'initialReduxState': {'gdp': {'building': {'ungroupedUnits': SAMPLE_LISTINGS}}}}}}
    }
    listings = extract_details(json_without_floorplans)
    assert len(listings) == 2
    assert listings[0]["baths"] == 2

#  Test get_details_info
def test_get_details_info():
    listing_info = get_details_info(SAMPLE_LISTINGS)
    assert len(listing_info) == 3  # 2 entries for first listing, 1 for second
    assert listing_info[0]["price"] == 1500
    assert listing_info[1]["price"] == 1300
    assert listing_info[2]["price"] == 1100

def test_get_listing_info_price_handling():
    listing_with_price = [{"listingType": "FOR_RENT", "beds": 1, "baths": 1, "sqft": 500, "price": 800}]
    result = get_details_info(listing_with_price)
    assert result[0]["price"] == 800
