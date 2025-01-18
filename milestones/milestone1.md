# :snowflake: CHIffordable :house:

## Members :couple::couple:

- María José Reyes  <mjreyes13@uchicago.edu>
- Daniela Ayala <danayala@uchicago.edu>
- Agustín Eyzaguirre <aeyzaguirre@uchicago.edu>
- José Manuel Cardona <jmcarias@uchicago.edu>

## Abstract :page_with_curl:

According to the Illinois Policy Institute, approximately 42% of Chicago low-income residents are burdened by housing costs that exceed 30% of their income and “22% pay more than half of their income”. Additionally, 78% of Chicago residents say that the city lacks sufficient affordable housing and the City of Chicago has identified “an affordable housing gap of around 120,000 homes and 240,000 rental units” [^1].

This project seeks to identify neighborhoods where low-income families can afford rental housing within a specified income percentage threshold. Leveraging data analysis and geospatial mapping, it will also explore these neighborhoods' demographic, economic, and social characteristics, along with public service availability. The findings aim to provide actionable insights for policymakers and community stakeholders, offering a comprehensive resource for addressing Chicago's affordable housing crisis.

## Preliminary Data Sources :computer:

### Data Source #1: Community Data Snapshots 2024 from the Chicago Metropolitan Agency for Planning (CMAP)

- A URL to the data source: [CMAP](https://datahub.cmap.illinois.gov/datasets/CMAPGIS::community-data-snapshots-2024/explore?layer=0) 
- Is the data coming from a webpage, bulk data, or an API?
Data comes from an API that is displayed by CMAP.
- Are there any challenges or uncertainty about the data at this point?
The data available in this source characterizes all 77 communities in Chicago with economic and demographic data. Yet, we see a challenge in merging this database with others because this one identifies each community through it’s name, and not with postal codes as expected. Yet, we think this isn’t a significant challenge because with some research we can identify each community with postal codes.

### Data Source #2: Zillow - Marketplace for housing (Ecommerce)
- A URL to the data source: [Ecommerce](https://www.zillow.com/chicago-il/rent-houses/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-88.2828080184946%2C%22east%22%3A-87.06057901458836%2C%22south%22%3A41.559915483636956%2C%22north%22%3A42.17860982259146%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A17426%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22priorityscore%22%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D) 
- Is the data coming from a webpage, bulk data, or an API?
API
- Are there any challenges or uncertainty about the data at this point?
The data includes Rental prices and characteristics. We would need to normalize data prices in a time period. 

### Data Source #3: Google Maps Platforms
- A URL to the data source: [Google Maps Platforms](https://developers.google.com/maps) 
- Is the data coming from a webpage, bulk data, or an API?
API
- Are there any challenges or uncertainty about the data at this point?
This data includes access to maps, direction geocoding and other different features of Chicago’s gentrification. This will be useful to identify the different characteristics of the neighborhoods and access to services people might have depending on tier location

### Data Source #4: Livability Index from American Association of Retired Persons (AARP)
- A URL to the data source: [AARP](https://livabilityindex.aarp.org/search/Chicago,%20Illinois,%20United%20States)
- Is the data coming from a webpage, bulk data, or an API?
API
- Are there any challenges or uncertainty about the data at this point?
This data provides scores and metrics in different variables related to measuring the quality of life for people. Including indicators for categories such as housing, neighborhood, transportation,environment, etc. This will be helpful to understand the environment where people are living. 

## Preliminary Project Plan 👷

1. Data Extraction
 - Extract socio-economic characteristics of the CMAP database.
 - Extract the apartment rentals listed on Zillow to extract relevant data (Postal Code, Sqft, Rooms, Price)

2. API Integration
 - Create the API call from google Maps using geographical data

3. Data Merging and KPI Definition
 - Merge the three sources of data CMAP, Zillow Google Maps
 - Define KPIs to display in the final visualization.

4. Visualization and User Interface
 - Create dynamic visualizations that allow users to filter by income and percentage they are willing to spend on Rent. The map should display characteristics (air quality, livability index, among others)
 - Design and implement the user interface (UI) for the visualization platform.


[^1]: https://www.illinoispolicy.org/press-releases/housing-unaffordability-on-the-rise-one-third-of-illinoisans-pay-over-30-of-their-income-on-housing/



## Questions

A **numbered** list of questions for us to respond to.
