import time
import httpx
from urllib.parse import urlparse

ALLOWED_DOMAINS = ("https://www.zillow.com",)
REQUEST_DELAY = 0.1 

def make_request(url):
    """
    Make a request to `url` and return the raw response.

    This function ensure that the domain matches what is expected
    and that the rate limit is obeyed.
    """
    # check if URL starts with an allowed domain name
    for domain in ALLOWED_DOMAINS:
        if url.startswith(domain):
            break
    else:
        # note: this else is indented correctly, it is a less-commonly used
        # for-else statement.  the condition is only met if the for loop
        # *never* breaks, i.e. no domains match
        raise ValueError(f"can not fetch {url}, must be in {ALLOWED_DOMAINS}")
    
    time.sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    resp = httpx.get(url)
    print(f"The status of the Fetching is: {resp.status}")
    resp.raise_for_status()
    return resp


