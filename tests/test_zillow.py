import pytest

from extracting.zillow_details import extract_listings, get_listing_info, get_prices, get_details_info
from extracting.zillow import extract_listings, get_listing_info, nextpage_from_xpath, one_zipcode_scrape

# Sample JSON Data for extract_listings
SAMPLE_ZILLOW_JSON = {
    'props': {
        'pageProps': {
            'searchPageState': {
                'cat1': {
                    'searchResults': {
                        'listResults': [
                            {
                                "address": "123 Main St",
                                "detailUrl": "/homedetails/123-Main-St",
                                "statusType": "For Rent",
                                "latLong": {"latitude": 41.0, "longitude": -87.0},
                                "addressZipcode": "60601",
                                "price": "$1,500",
                                "area": 800,
                                "id": "12345",
                                "beds": 2,
                                "baths": 1
                            }
                        ]
                    }
                }
            }
        }
    }
}

# Sample HTML for nextpage_from_xpath
SAMPLE_HTML_WITH_NEXT = '''
<html>
    <body>
        <a rel="next" title="Next page" href="/rentals/page2/"></a>
    </body>
</html>
'''

SAMPLE_HTML_LAST_PAGE = '''
<html>
    <body>
        <p>No next page available</p>
    </body>
</html>
'''

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

# General Zillow listig tests
# 1. Test extract_listings
def test_extract_listings():
    listings = extract_listings(SAMPLE_ZILLOW_JSON)
    assert isinstance(listings, list)
    assert len(listings) == 1
    assert listings[0]["address"] == "123 Main St"

def test_extract_listings_empty():
    empty_json = {'props': {'pageProps': {'searchPageState': {'cat1': {'searchResults': {'listResults': []}}}}}}
    listings = extract_listings(empty_json)
    assert listings == []

def test_extract_listings_invalid_json():
    with pytest.raises(KeyError):
        extract_listings({})  

# 2. Test get_listing_info
def test_get_listing_info():
    listing_info = get_listing_info(SAMPLE_ZILLOW_JSON['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults'][0])
    assert listing_info["address"] == "123 Main St"
    assert listing_info["clean_price"] == "1500"
    assert listing_info["bedrooms"] == 2

def test_get_listing_info_missing_fields():
    listing_info = get_listing_info({})
    assert listing_info["address"] == ""
    assert listing_info["clean_price"] is None

def test_get_listing_info_price_cleanup():
    listing_info = get_listing_info({"price": "$2,000/mo"})
    assert listing_info["clean_price"] == "2000"

# 3. Test nextpage_from_xpath
def test_nextpage_from_xpath():
    next_url = nextpage_from_xpath(SAMPLE_HTML_WITH_NEXT)
    assert next_url.endswith("/rentals/page2/")

def test_nextpage_from_xpath_last_page():
    next_url = nextpage_from_xpath(SAMPLE_HTML_LAST_PAGE)
    assert next_url is None

def test_nextpage_from_xpath_invalid_html():
    with pytest.raises(AttributeError):
        nextpage_from_xpath("<html></html>")

# Listing Details tests
# 1. Test extract_listings
def test_extract_listings():
    listings = extract_listings(SAMPLE_JSON_DETAILS)
    assert isinstance(listings, list)
    assert len(listings) == 2
    assert listings[0]["beds"] == 2
    assert listings[1]["sqft"] == 600

def test_extract_listings_no_floorplans():
    json_without_floorplans = {
        'props': {'pageProps': {'componentProps': {'initialReduxState': {'gdp': {'building': {'ungroupedUnits': SAMPLE_LISTINGS}}}}}}
    }
    listings = extract_listings(json_without_floorplans)
    assert len(listings) == 2
    assert listings[0]["baths"] == 2

def test_extract_listings_invalid_json():
    assert extract_listings({}) == []

# 2. Test get_listing_info
def test_get_listing_info():
    listing_info = get_listing_info(SAMPLE_LISTINGS)
    assert len(listing_info) == 3  # 2 entries for first listing, 1 for second
    assert listing_info[0]["price"] == 1500
    assert listing_info[1]["price"] == 1300
    assert listing_info[2]["price"] == 1100

def test_get_listing_info_missing_fields():
    listing_info = get_listing_info([{}])
    assert listing_info == []

def test_get_listing_info_price_handling():
    listing_with_price = [{"listingType": "FOR_RENT", "beds": 1, "baths": 1, "sqft": 500, "price": 800}]
    result = get_listing_info(listing_with_price)
    assert result[0]["price"] == 800

# 3.Test get_details_info 
def test_get_details_info(monkeypatch):
    def mock_get_prices(url):
        return [{"price": 1400, "beds": 2, "baths": 1, "sqft": 750}]
    
    monkeypatch.setattr("zillow_details.get_prices", mock_get_prices)
    
    details = get_details_info(SAMPLE_LISTING_DICT)
    assert len(details) == 1
    assert details[0]["price"] == 1400
    assert details[0]["address"] == "123 Main St"

def test_get_details_info_no_data(monkeypatch):
    monkeypatch.setattr("zillow_details.get_prices", lambda url: [])
    assert get_details_info(SAMPLE_LISTING_DICT) == []

def test_get_details_info_multiple_apartments(monkeypatch):
    def mock_get_prices(url):
        return [{"price": 1500, "beds": 3, "baths": 2, "sqft": 900},
                {"price": 1200, "beds": 2, "baths": 1, "sqft": 700}]
    
    monkeypatch.setattr("zillow_details.get_prices", mock_get_prices)
    
    details = get_details_info(SAMPLE_LISTING_DICT)
    assert len(details) == 2
    assert details[0]["beds"] == 3
    assert details[1]["price"] == 1200


if __name__ == "__main__":
    pytest.main()