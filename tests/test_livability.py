import pytest
import time
import httpx
import lxml.html
import regex  as re
import csv
import os
import json
from unittest.mock  import patch
from pathlib import Path
from extracting.livability import make_table_request, livindex_by_zc, extract_next_chars


# Step 1: Path for functions 
livability_scrape = Path(__file__).parent.parent / "extracting" / "livability.py"

# Step 2: Creating a fixture in pytest to generate a simulation response from the API
@pytest.fixture

def mock_response():
    """
    Simulating a Json response from the API
    """
    return {
        "score_prox": 75,
        "score_engage": 80,
        "score_env": 65,
        "score_health": 90,
        "score_house": 70,
        "score_opp": 85,
        "score_trans": 60
    }
# Step 3: Unitary probing to verify that make_table_request returns correct data
@patch("extracting.livability.extract_next_chars")
@patch("httpx.Client.get")
def test_make_table_request_success(mock_get, mock_extract_next_chars, mock_response):
    """
    Testing function make_table_request is returning data 
    """
# Step 1: Simulating a HTTP  with code 200 and Json content
    mock_http_response = httpx.Response(
        status_code = 200, content =json.dumps(mock_response).encode("utf-8"))
    # Step 2: CSetting up mock to return the following response 
    mock_get.return_value = mock_http_response  
    # Step 4: Simulating the extract_next_chars behaviour that brings JSON values
    mock_extract_next_chars.return_value = mock_response  

    # Step 5: Calling 'make_table_request' with a mock zip code
    mock_zip_code = "60601"
    result = make_table_request(mock_zip_code)
    # Step 6: Verifyng that th result matches the expected response
    assert result == mock_response, f"Expected{mock_response}, but got {result}"
# Unitary probing to verify 'livindex_by_zc' with valid zip codes
@patch("extracting.livability.make_table_request")
def test_livindex_by_zc_valid(mock_make_table_request):
    """
    Testing valid zipcodes
    """
    # Step 1: Defining the expected response for 2 different zip codes 
    mock_make_table_request.side_effect = [
        {"score_health": 90, "score_env": 85},
        {"score_health": 80, "score_env": 75}
    ]
    # Step 2: Mock zip codes 
    zip_codes = ["60601", "60602"]

    # Step 3; Calling function 'livindex_by_zc'
    result = livindex_by_zc(zip_codes)
    # Step 4: Defining the expected result, including zip codes 
    expected = [
        {"score_health": 90, "score_env": 85, "zip_code": "60601"},
        {"score_health": 80, "score_env": 75, "zip_code": "60602"}
    ]
    # Step 5: verifying that the returned result is the same as expected 
    assert result == expected, f"Expected{expected}, but obtained {result}"

@patch("extracting.livability.make_table_request")
def test_livindex_by_zc_empty_list(mock_make_table_request):
    result = livindex_by_zc([])
    assert result == [], "was expecting an empty list"

@patch("extracting.livability.make_table_request")
def test_livindex_by_zc_invalid_zip(mock_make_table_request):
    # Step 1: Handling None return 
    mock_make_table_request.return_value = None
    # Step 2: Defining invalid zip codes
    zip_codes = ["99999"]
    # Step 4: Calling the function 
    result = livindex_by_zc(zip_codes)
    # Step 5: Defining the expected outcome
    expected = [{"zip_code": "99999"}]
    # Step 6: verifying that the result coincides with the expected
    assert result == expected, f"Expected {expected}, but obtained {result}"
    
