# :snowflake: CHIffordable :house:

The city of Chicago has identified “an affordable housing gap of around 120,000 homes and 240,000 rental units”[^1], 42% of its residents are burdened by housing costs that exceed 30% of their income and “22% pay more than half of their income”. 

This project seeks to identify places where low-income families can afford rental housing within a specified income and a percentage of their income they are willing to spend on rent. Leveraging data analysis and geospatial mapping, it will also explore these neighborhoods' demographic, economic, and social characteristics. The findings aim to provide actionable insights for policymakers and community stakeholders, offering a comprehensive resource for addressing Chicago's affordable housing crisis.

## How to run run this project? :arrow_forward:

1. [Install UV to Local Machine](https://docs.astral.sh/uv/getting-started/installation/)

2. Clone the Project
```bash
git clone
```

3. Install Virtual Environment and Dependencies
```bash
uv sync
```

4. Run the application

```bash
uv run main.py
```

## Demo :beetle:

[![Watch the video](https://img.youtube.com/vi/ecBzrd5wgFA/0.jpg)](https://www.youtube.com/watch?v=ecBzrd5wgFA)


## Structure of Software :hammer_and_wrench:
This project is structured in the following sections:

- Data Extraction (Extracting Module):
  - CMAP: Data is retrieved via an API in JSON format, providing demographic and economic insights.
  - AARP: Web scraping extracts livability scores, and missing ZIP codes are manually supplemented.
  - Zillow: Web scraping is used to collect rental listings, including price, size, and location. 
- Data Processing (Extracted Data Module):
  - CMAP data is processed to compute age and racial distributions as percentages.
  - Zillow listings are cleaned, ensuring accurate price formatting and geolocation data.
  - Livability scores from AARP are extracted and structured.
  - All datasets are standardized for integration.
- Testing (Tests Module): 
  - Unit tests ensure data integrity, verifying total population percentages and livability score accuracy.
  - Mock responses simulate API calls and web scraping to validate extraction functions.
  - CSV outputs are checked to confirm proper formatting and completeness.
- Visualization & Interaction (App Module):
  - An interactive Dash web application is created to explore affordable housing options.
  - Users input their annual income and rent percentage, filtering affordable listings dynamically.
  - Maps display rental listings, demographic distributions, and livability scores.
  - Clicking on a community reveals detailed insights, including rent prices, racial composition, and livability index scores.

## Data Sources :computer:

### Data Source #1: Zillow - Marketplace for housing [Zillow](https://www.zillow.com/chicago-il/rent-houses/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-88.2828080184946%2C%22east%22%3A-87.06057901458836%2C%22south%22%3A41.559915483636956%2C%22north%22%3A42.17860982259146%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A17426%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22priorityscore%22%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D)

Zillow is an online real estate marketplace that provides information on properties for sale, rent, and mortgage financing. From Zillow, we use property listing details such as price, size, location, number of bedrooms and bathrooms.

### Data Source #2: Community Data Snapshots 2024 from the Chicago Metropolitan Agency for Planning [CMAP](https://datahub.cmap.illinois.gov/datasets/CMAPGIS::community-data-snapshots-2024/explore?layer=0)

The Community Data Snapshots (CDS) project collects a variety of demographic, housing, employment, land use, and other data for northeastern Illinois. These tables contain information for counties, municipalities, and Chicago community areas (CCAs). The primary source is data from the U.S. Census Bureau’s 2022 American Community Survey program.

### Data Source #3: Livability Index from American Association of Retired Persons [AARP](https://livabilityindex.aarp.org/search/Chicago,%20Illinois,%20United%20States)

The AARP Livability Index is created from more than 50 unique sources of data across the seven livability categories. Using these metrics and policies, the AARP Livability Index scores communities by looking at how livable each neighborhood is within the community. The categories each provide important pieces of the picture of livability in a community: Housing, Neighborhood characteristics, Transportation, Environment, Health, Engagement and Opportunities.

## Scraping Details :computer:

Requesting data from Zillow requires to update the headers form the website.
Last update 03.09.2025

Once you have valid headers, we include a script to regularly scrape data from Zillow. Although we scraped listings by zipcode. Each zipcode may include its own scraper for listings that cointaing multiple apparments and prices. 

Update the listings database using uv run python -m extracting/zillow.py . This will scrape all zipcodes from Chicago and update the data in Zillow.csv file

## Contributors :couple::couple:

| Member        | Lead           | Contributions  |
| ------------- |-------------| ----- |
| Daniela Ayala <danayala@uchicago.edu>      | Zillow scraper and extracting utils and correspondent test functions | Data visualizations |
| José Manuel Cardona <jmcarias@uchicago.edu>      | Data reconciliation, data visualizations, interactive app and App utils tests      |   AARP scraping |
| Agustín Eyzaguirre <aeyzaguirre@uchicago.edu> | CMAP API calls and       |    Cont |
| María José Reyes  <mjreyes13@uchicago.edu> | AARP scaping and      |    Cont |

## Acknowledgments

CAPP 122 Instructor - James Turk

CAPP 122 Project TA - Stacey George

[^1]: https://www.illinoispolicy.org/press-releases/housing-unaffordability-on-the-rise-one-third-of-illinoisans-pay-over-30-of-their-income-on-housing/
