import pytest
import json
import httpx
import os
import pandas as pd
from extracting.utils import (
    complete_link,
    fetch_page,
    parse_script_content,
    save_to_csv,
)


SAMPLE_HTML = """
<html>
    <script id="__NEXT_DATA__">{"key": "value"}</script>
</html>
"""

SAMPLE_HTML_NO_SCRIPT = """
<html>
    <body><p>No script tag here</p></body>
</html>
"""

SAMPLE_HTML_INVALID_JSON = """
<html>
    <script id="__NEXT_DATA__">Invalid JSON</script>
</html>
"""

SAMPLE_LISTINGS = [
    {"address": "123 Main St", "price": 1500, "beds": 2, "baths": 1},
    {"address": "456 Oak St", "price": 1200, "beds": 1, "baths": 1},
]


# complete_link
def test_complete_link_full_url():
    base_url = "https://www.zillow.com"
    url = "https://www.zillow.com/homedetails/123-Main-St"
    assert complete_link(base_url, url) == url, (
        f"Expected {url} but got {complete_link(base_url, url)}"
    )


def test_complete_link_partial_url():
    base_url = "https://www.zillow.com"
    url = "/homedetails/123-Main-St"
    expected = "https://www.zillow.com/homedetails/123-Main-St"
    assert complete_link(base_url, url) == expected, (
        f"Expected {expected} but got {complete_link(base_url, url)}"
    )


def test_complete_link_empty():
    base_url = "https://www.zillow.com"
    url = None
    assert complete_link(base_url, url) is None, "Expected None but got something else"


# parse_script_content
def test_parse_script_content_valid():
    result = parse_script_content(SAMPLE_HTML)
    assert result == {"key": "value"}, f"Expected parsed JSON but got {result}"


def test_parse_script_content_missing():
    result = parse_script_content(SAMPLE_HTML_NO_SCRIPT)
    assert result == {}, f"Expected empty dict but got {result}"


def test_parse_script_content_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        parse_script_content(SAMPLE_HTML_INVALID_JSON)


# save_to_csv
@pytest.fixture
def sample_listings():
    return [
        {"address": "123 Main St", "price": 1500, "beds": 2, "baths": 1},
        {"address": "456 Oak St", "price": 1200, "beds": 1, "baths": 1},
    ]


def test_save_to_csv(sample_listings, tmpdir):
    filename = "test_csv.csv"
    file_cols = ["address", "price", "beds", "baths"]
    save_path = str(tmpdir)

    save_to_csv(sample_listings, filename, file_cols, save_path)

    full_path = os.path.join(save_path, filename)
    assert os.path.exists(full_path), (
        f"Expected file to exist at {full_path} but it was not found"
    )

    # Read CSV and check contents
    df = pd.read_csv(full_path)
    assert len(df) == 2, f"Expected 2 rows but got {len(df)}"
    assert list(df.columns) == file_cols, (
        f"Expected columns {file_cols} but got {list(df.columns)}"
    )


def test_fetch_page_success(httpx_mock):
    """Test that fetch_page returns the correct response when the request is successful."""
    url = "https://example.com"
    expected_content = "<html><body>Hello, world!</body></html>"

    # Mock response
    httpx_mock.add_response(url=url, text=expected_content, status_code=200)

    result = fetch_page(url).text
    print(result)

    assert result == expected_content  # Ensure the response is correctly returned


def test_fetch_page_http_error(httpx_mock):
    """Test that fetch_page raises HTTPStatusError when the response is not 200."""
    url = "https://example.com"

    # Mock a 404 error
    httpx_mock.add_response(url=url, status_code=404)

    with pytest.raises(httpx.HTTPStatusError):
        fetch_page(url)


def test_fetch_page_with_custom_headers(httpx_mock):
    """Test that fetch_page correctly sends custom headers."""
    url = "https://example.com"
    expected_content = "Test response"
    custom_headers = {"User-Agent": "CustomAgent"}

    # Mock response
    httpx_mock.add_response(url=url, text=expected_content, status_code=200)

    result = fetch_page(url, headers_input=custom_headers).text

    assert result == expected_content  # Ensure correct response is returned


def test_fetch_page_invalid_url():
    """Test that fetch_page raises an error for an invalid URL."""
    url = "invalid_url"

    with pytest.raises(httpx.RequestError):
        fetch_page(url)
