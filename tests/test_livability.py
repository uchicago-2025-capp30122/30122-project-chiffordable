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


# Path for functions 
livability_scrape = Path(__file__).parent.parent / "extracting" / "livability.py"

# Creating a mock response for table scores
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

@patch("extracting.livability.extract_next_chars")
@patch("httpx.Client.get")
def test_make_table_request_success(mock_get, mock_extract_next_chars, mock_response):
    """
    Testing function make_table_request is returning data 
    """

    mock_http_response = httpx.Response(
        status_code = 200, content =json.dumps(mock_response).encode("utf-8"))
    
    mock_get.return_value = mock_http_response  

    mock_extract_next_chars.return_value = mock_response  

    # Sample zipcodes for tests
    mock_zip_code = "60601"
    result = make_table_request(mock_zip_code)

    assert result == mock_response, f"Expected{mock_response}, but got {result}"

@patch("extracting.livability.make_table_request")
def test_livindex_by_zc_valid(mock_make_table_request):
    """
    Testing valid zipcodes
    """

    mock_make_table_request.side_effect = [
        {"score_health": 90, "score_env": 85},
        {"score_health": 80, "score_env": 75}
    ]
    
    zip_codes = ["60601", "60602"]
    result = livindex_by_zc(zip_codes)

    expected = [
        {"score_health": 90, "score_env": 85, "zip_code": "60601"},
        {"score_health": 80, "score_env": 75, "zip_code": "60602"}
    ]
    assert result == expected, f"Expected{expected}, but obtained {result}"

@patch("extracting.livability.make_table_request")
def test_livindex_by_zc_empty_list(mock_make_table_request):
    result = livindex_by_zc([])
    assert result == [], "was expecting an empty list"

@patch("extracting.livability.make_table_request")
def test_livindex_by_zc_invalid_zip(mock_make_table_request):

    mock_make_table_request.return_value = None

    zip_codes = ["99999"]
    result = livindex_by_zc(zip_codes)

    expected = [{"zip_code": "99999"}]
    assert result == expected, f"Expected {expected}, but obtained {result}"
    
