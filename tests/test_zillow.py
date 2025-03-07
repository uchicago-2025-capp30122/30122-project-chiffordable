import pytest
from extracting.zillow import extract_listings, get_listing_info, nextpage_from_xpath

# Sample JSON Data for extract_listings
SAMPLE_ZILLOW_JSON = {
    "props": {
        "pageProps": {
            "searchPageState": {
                "cat1": {
                    "searchResults": {
                        "listResults": [
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
                                "baths": 1,
                            }
                        ]
                    }
                }
            }
        }
    }
}

# Sample HTML for nextpage_from_xpath
SAMPLE_HTML_WITH_NEXT = """
<html>
    <body>
        <a rel="next" title="Next page" href="/rentals/page2/"></a>
    </body>
</html>
"""

SAMPLE_HTML_LAST_PAGE = """
<html>
    <body>
        <p>No next page available</p>
    </body>
</html>
"""


# 1. Test extract_listings
def test_extract_listings():
    listings = extract_listings(SAMPLE_ZILLOW_JSON)
    assert isinstance(listings, list)
    assert len(listings) == 1
    assert listings[0]["address"] == "123 Main St"


def test_extract_listings_empty():
    empty_json = {
        "props": {
            "pageProps": {
                "searchPageState": {"cat1": {"searchResults": {"listResults": []}}}
            }
        }
    }
    listings = extract_listings(empty_json)
    assert listings == []


def test_extract_listings_invalid_json():
    with pytest.raises(KeyError):
        extract_listings({})


# 2. Test get_listing_info
def test_get_listing_info():
    listing_info = get_listing_info(
        SAMPLE_ZILLOW_JSON["props"]["pageProps"]["searchPageState"]["cat1"][
            "searchResults"
        ]["listResults"][0]
    )
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
