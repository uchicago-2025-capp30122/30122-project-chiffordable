# :snowflake: CHIffordable :house:

## Members :couple::couple:

- María José Reyes  <mjreyes13@uchicago.edu>
- Daniela Ayala <danayala@uchicago.edu>
- Agustín Eyzaguirre <aeyzaguirre@uchicago.edu>
- José Manuel Cardona <jmcarias@uchicago.edu>

## Abstract :page_with_curl:

The city of Chicago has identified “an affordable housing gap of around 120,000 homes and 240,000 rental units”[^1], 42% of its residents are burdened by housing costs that exceed 30% of their income and “22% pay more than half of their income”. 

This project seeks to identify neighborhoods where low-income families can afford rental housing within a specified income and a percentage of their income they want/can spend on rent. Leveraging data analysis and geospatial mapping, it will also explore these neighborhoods' demographic, economic, and social characteristics, along with public service availability. The findings aim to provide actionable insights for policymakers and community stakeholders, offering a comprehensive resource for addressing Chicago's affordable housing crisis.

## Data Reconciliation Plan :shipit:

We identified 4 different data sources that will be merged using geolocation data and/or community location indicators, such as Zip code and Community ID. The following figure represents the merging plan and variables that will allow us to create a centralized database for the project.

![alt text](https://github.com/uchicago-2025-capp30122/30122-project-chiffordable/blob/main/milestones/media/data_reconciliation.png?raw=true)

## Data Sources :computer:

### Data Source #1: Community Data Snapshots 2024 from the Chicago Metropolitan Agency for Planning (CMAP)
- A URL to the data source: [CMAP](https://datahub.cmap.illinois.gov/datasets/CMAPGIS::community-data-snapshots-2024/explore?layer=0)

- Is the data coming from a webpage, bulk data, or an API?
  
    Data comes from an API that is displayed by CMAP [CMAP API](https://services5.arcgis.com/LcMXE3TFhi1BSaCY/arcgis/rest/services/Community_Data_Snapshots_2024/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson). Also, the information can be downloaded to a CSV file from the CMAP webpage.

- Are there any challenges or uncertainty about the data at this point?
  
    The data available in this source characterizes all 77 communities in Chicago, counties and municipalities with economic and demographic data. A potential challenge to merge this data with others is the identifier used for the observation variables (in our case communities), since this dataset identifies each community through its name and GEOID (code for each community), and not with a ZIP Code, as the others sources of information we are using.
    For us it will be important to think how to merge this database with the other data we are working with. The initial idea would be to find the zip codes each community contains to merge them with the other information.

- How many records (rows) does your data set have?
  
    It has 77 rows, one for each of the 77 Chicago communities.

- Write a few sentences about your exploration of the data set.
  
    From the exploratory analysis of the data, we could observe that the type of data are mostly float type, and that missing data will not be a major challenge because the dataset was previously cleaned by the CMAP data team. Also, for some of the columns provided the variables that are being measured are not clear for us, to solve this problem we sent a request to the Chicago Metropolitan Agency for Planning (CMAP) to verify if they can send us a glossary of the data, to have a better interpretation of it.


### Data Source #2: Zillow - Marketplace for housing (Ecommerce)
- A URL to the data source: [Zillow](https://www.zillow.com/chicago-il/rent-houses/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-88.2828080184946%2C%22east%22%3A-87.06057901458836%2C%22south%22%3A41.559915483636956%2C%22north%22%3A42.17860982259146%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A17426%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22priorityscore%22%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D)

- Is the data coming from a webpage, bulk data, or an API?
  
    The data comes from the Zillow web page and from each property’s webpage. We will scrape each property’s webpage from the city of Chicago or from a specific set of ZIP codes.

- Are there any challenges or uncertainty about the data at this point?
  
    The data includes Rental prices and characteristics of the property. We can get the whole address and location information such as latitude, longitude and zip code, which we can use for merging with other data sets.
    However,in some areas of Chicago Zillow doesn’t have any properties listed, so one of the main challenges of this data will be how to complete the dataset for these areas. We can complement Zillow rental prices with other housing marketplaces or with the estimated average rental from the CCA dataset.


- How many records (rows) does your data set have?
  
    As of today, in Chicago there are 13,849 rentals available on the Zillow webpage that will change with time. The number of listings varies from zip code to zip code. Zillow only includes current available properties.

- Write a few sentences about your exploration of the data set.
  
    We can get the following data from each property:
  1. Property name
  2. Property description: type of property, building composition, access to facilities such as schools –distance–, access disability features, building features and appliances, built year, type of heating, AC, parking, lot size, water source, room description.
  3. Location features: Latitude and Longitude, Zip Code, Address (with Maps link), County ID.
  4. Rental and listing price, price per sq/feet.
  5. Community features
  6. School district.
  7. Tax history and price change rates
  8. Zillow value estimate
  9. Days on Zillow
 
- Write a few sentences about your exploration of the data set.

    There are two steps for exploring the Zillow webpage:
  1. Web Scrape the main page of Zillow to extract the urls for every property in the city of Chicago.
  2. Web Scrape every individual property to get the characteristics mentioned before.
    We already got the scraping for the general Zillow webpage and the exploration of individual properties. As of right now, our functions are able to scrape Zillow data without any problems. The first function pulls data with links for all of the Zillow listings, when a City and/or ZIP code is provided. The second function takes the link of a specific listing and scrapes all of the data listed in the previous section. This part will become important to be able to extract data even when changing positions for each property (positional scraping). 

### Data Source #3: Google Maps Platforms
- A URL to the data source: [GOOGLE MAPS](https://developers.google.com/maps/documentation/places-insights/overview#:~:text=The%20Places%20Insights%20API%20empowers,potential%20locations%20for%20new%20branches.)

- Is the data coming from a webpage, bulk data, or an API?
    The data comes the Google Places Insights API
  
- Are there any challenges or uncertainty about the data at this point?
    The Place Insights API is in the pre-GA stage, meaning that Google is testing this product. Using an API that’s in this stage has certain advantages, risks and constraints. The main ones are:
  1. Google doesn’t charge until the API goes live. Until then, there’s no possible way to know if the usage of this data will have a cost or not, and if it does so, how much it will be.
  2. This type of APIs have limited support and aren’t covered by SLAs.
  3. Since Google is testing this product, the final API may not be compatible with the code we are going to use to call the API. This may lead to having our program crash or having to re-code our program every time the API updates until Google has the final live version.

- How many records (rows) does your data set have?
    It will depend on the parameters given to the API.

- How many properties (columns) does your data set have?
    It will depend on the parameters given to the API.

- Write a few sentences about your exploration of the data set.
    - From a specific location or Zip Code, Google delivers the number of services that are located within a radio, region or polygon. The services that are to be counted will depend on the ones that are specified when calling the API. First, we will search for supermarkets, drugstores, High Schools, hospitals, parks, financial services, and others. This will be useful to identify the different characteristics of the neighborhoods and access to services people might have depending on their location. 
    - To make a request in places ID, there are different key functions: (a) Count places (determine the number of places that match specific criteria), (b) Retrieve Place Details (obtain the name of places that meet specified filters), (c) Flexible Filter (apply comprehensive filter to get precise insights).
    - IDs: it uniquely identifies a place in the Google Places database and on Google Maps. For our study case, the first ID we would be using would be for the Chicago city, which is: ChIJ7cv00DwsDogRAMDACa2m4K8 Chicago, IL, USA
    - Parameters required for making requests:
    -   There are two insight types: (a) INSIGHT_COUNT: Returns the number of places matching filter criteria (b) INSIGHT_PLACES: Returns the place IDs matching the filter criteria (only for counts 100 or less).
    -   Location filters, has three types of filters to define an area (circle, region or polygon)[^2][^3].

### Data Source #4: Livability Index from American Association of Retired Persons (AARP)

- A URL to the data source: [AARP](https://livabilityindex.aarp.org/search/Chicago,%20Illinois,%20United%20States)

- Is the data coming from a webpage, bulk data, or an API?
    Data comes from a webpage and contains different Livability Index for different locations (Including housing index, engagement, health, environment, etc)

- Are there any challenges or uncertainty about the data at this point?
    The data level is Zip Code. We can merge with other detailed data (Zillow) that includes the whole address. We are trusting in the indexes to obtain the data of the Zipcode.

- How many records (rows) does your data set have?
    We have as many rows as zipcodes. Chicago IL has 91 Zip codes.

- How many properties (columns) does your data set have?

    1. General livability Index
    2. Housing Index (Affordability and Access)
    3. Neighborhood (Proximity and Security)
    4. Transportation (Safety and Convenience)
    5. Environment (Clean Air and Water)
    6. Health (Prevention, Access and Quality)
    7. Engagement (Civic and Social Involvement)
    8. Opportunity (Inclusion and Possibilities)
    9. Total Population
    10. Racial composition: Black/African American, Asian American, Hispanic/Latino, White, American Indian/Alaska Native, Hawaiian, Two or More Races, Some Other Race.
    11. Age composition: Age 50+, Age 65+
    12. % of the population with a disability
    13. Life Expectancy
    14. Households Without a Vehicle
    15. Median Household Income
    16. % of the population with income below poverty
    17. Upward Mobility

## Project Plan :construction_worker:
  1. Web Scrape Zillow and its correspondent webpages to have real data from rental prices and characteristics within the city of Chicago.
  2. Web Scrape AARP with the livability index of the 91 Zip Codes of the city of Chicago.
  3. We will merge Zillow and AARP through Zip Codes. Also, with steps 1-2 we can build an MVP that can characterize possible places to live in Chicago according to certain income and percentage of income to be spent on rent.
  4. Complete data of rental prices from areas that are not on Zillow with the information from the CCA of CMAP (Database 1). Also, we can complete the demographic characterization with variables that are not in the livability index. This data set will be merged with the previous ones through Zip Codes researched for each Chicago’s community name.
  5. Complete characterization of places to live with services displayed by API from Google (optional).
  6. Work on data visualization, UX and UI (Create dynamic visualizations that allow users to filter by income and percentage they are willing to spend on Rent. The map should display characteristics (air quality, livability index, among others)

### Short-term goal (due Feb 9) :calendar:
1. CMAP database:
    - Primary responsible: Agustín
    - Hellping: María José
2. Zillow:
    - Primary responsible: Daniela
    - Helping: José and María José
3. AARP:
    - Primary responsible: José
    - Helping: Daniela
4. Centralized database:
    - Primary responsible: María José
    - Helping: Agustín
  
## Questions :question:
  1. How should we handle missing rental data (from Zillow) for certain Chicago neighborhoods? Are there additional sources we should consider to supplement Zillow rental data?
  2. What visualization techniques will best communicate affordability and livability insights?
  3. From your perspective, is the API of Google a one we can rely on considering its risks of being in pre-GA stage?
  4. When scraping data from Zillow, we noticed that cookies are necessary headers for obtaining a 200 Request code (otherwise we get a 403). Do you have any recommendations for how to handle such situations?
  5. We found the following recommendations for scraping data from Zillow. From your experience, is there something else we should be aware of or that we should be cautious about?
      - Do not scrape at rates that could damage the website.
      - Do not scrape data that's not available publicly.
      - Do not store PII of EU citizens who are protected by GDPR.
      - Do not repurpose the entire public datasets which can be illegal in some countries.






[^1]: https://www.illinoispolicy.org/press-releases/housing-unaffordability-on-the-rise-one-third-of-illinoisans-pay-over-30-of-their-income-on-housing/
[^2]: For entities with defined polygonal boundaries such as parks or airports, the entity is considered to be within the search area if any part of its polygon intersects with the defined search area (circle, region, or custom polygon). The entity's center point does not need to be within the search area. More information can be found in: https://developers.google.com/maps/documentation/places-insights/request-parameters. 
[^3]: Important: The area for any location filter must be between 1556.86 square meters (approximately the size of a small city block) and 2 trillion square meters (approximately the size of Alaska). Requests with areas outside this range will return an INVALID_ARGUMENT error.



