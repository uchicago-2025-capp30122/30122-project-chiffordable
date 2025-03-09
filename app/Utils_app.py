from shapely.geometry import Point
import met_brewer

# ---------------------------- Color palette ----------------------------
colors_communities = met_brewer.met_brew(name="Tam", n=20, brew_type="continuous")
colors_details = met_brewer.met_brew(name="Tam", n=3, brew_type="discrete")

# ---------------------------- Text for descriptions --------------------
abstract_str = (
    "The city of Chicago has identified “an affordable housing gap of around 120,000 homes and 240,000 rental units”, "
    "42% of its residents are burdened by housing costs that exceed 30% of their income and “22% pay more than half of their income”.\n\n"
    "This project seeks to identify places where low-income families can afford rental housing within a specified income and a percentage of their income they are willing to spend on rent. "
    "Leveraging data analysis and geospatial mapping, it will also explore these neighborhoods' demographic, economic, and social characteristics. "
    "The findings aim to provide actionable insights for policymakers and community stakeholders, offering a comprehensive resource for addressing Chicago's affordable housing crisis."
)
instructions_str = """
    <h3>How to Use This App?</h3>
    <p><strong>CHI-ffordable</strong> is an interactive tool designed to help you explore affordable housing options in Chicago based on your income and rent preferences. Follow these steps to navigate the app:</p>
    
    <h4>1. Select Your Budget</h4>
    <ul>
        <li>Enter your <strong>annual income</strong> in the input box.</li>
        <li>Specify the <strong>percentage of income</strong> you’re willing to spend on rent.</li>
    </ul>
    
    <h4>2. Explore Affordable Housing Options</h4>
    <ul>
        <li>The interactive <strong>map</strong> will display communities and rental listings that match your budget.</li>
        <li><strong>Shaded areas</strong> represent community-level rent affordability.</li>
        <li><strong>Markers</strong> indicate individual listings that fall within your specified rent limit.</li>
    </ul>
    
    <h4>3. Click to View Community Details</h4>
    <ul>
        <li>Clicking on a <strong>community area</strong> will display its <strong>median rent</strong> and <strong>demographic information</strong> (age distribution, racial composition, and livability scores).</li>
        <li>Clicking on a <strong>listing</strong> will provide details about the rental unit, including a <strong>link to the Zillow listing</strong> for more information.</li>
    </ul>

    <h4>4. Navigate Through the App</h4>
    <ul>
        <li>Use the <strong>tabs at the top</strong> to explore different sections:</li>
        <ul>
            <li><strong>Home</strong>: Learn about the purpose of this tool.</li>
            <li><strong>Explore</strong>: Adjust your budget and view rental options.</li>
            <li><strong>About</strong>: Find information on data sources and acknowledgments.</li>
        </ul>
    </ul>

    <p>Start exploring and find an affordable home that fits your needs! 🚀</p>
"""

data_sources_str = [
    "- Zillow - Marketplace for housing:   \n"
    "  Zillow is an online real estate marketplace that provides information on properties for sale, rent, and mortgage financing.  \n"
    "  From Zillow, we use property listing details such as price, size, location, number of bedrooms, and bathrooms.  \n\n",
    "- Community Data Snapshots 2024 from the Chicago Metropolitan Agency for Planning (CMAP):  \n"
    "  The Community Data Snapshots (CDS) project collects a variety of demographic, housing, employment, land use, and other data for northeastern Illinois.  \n"
    "  These tables contain information for counties, municipalities, and Chicago community areas (CCAs).  \n"
    "  The primary source is data from the U.S. Census Bureau’s 2022 American Community Survey program.  \n\n",
    "- Livability Index from American Association of Retired Persons (AARP):  \n"
    "  The AARP Livability Index is created from more than 50 unique sources of data across seven livability categories.  \n"
    "  Using these metrics and policies, the AARP Livability Index scores communities by looking at how livable each neighborhood is within the community.  \n"
    "  The categories each provide important pieces of the picture of livability in a community: Housing, Neighborhood characteristics, Transportation, Environment, Health, Engagement, and Opportunities."
]

repo_str = (
    "https://github.com/uchicago-2025-capp30122/30122-project-chiffordable/tree/main"
)

authors_str = (
    "- Daniela Ayala - danayala@uchicago.edu  \n"
    "- José Manuel Cardona - jmcarias@uchicago.edu  \n"
    "- Agustín Eyzaguirre - aeyzaguirre@uchicago.edu  \n"
    "- María José Reyes - mjreyes13@uchicago.edu"
)


# ---------------------------- Utility functions ------------------------
def gdf_to_geojson(gdf):
    """
    Takes a GeoDataframe and transforms it into a geojson for choropleth map

    Inputs:
        - gdf: a GeoDataframe with the attributes
    Returns:
        - geojson file
    """
    features = []
    # Takes every row in the GeoDataframe and extracts its features:
    #   - geometry making sure it is ready for plot
    #   - properties: GEOG (name) and median_rent
    for _, row in gdf.iterrows():
        feature = {
            "type": "Feature",
            "geometry": row["geometry"].__geo_interface__,
            "properties": {"GEOG": row["GEOG"], "median_rent": row["median_rent"]},
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}


def get_community_from_point(gdf_dataframe, lat, lon):
    """
    Obtains the community details based on latitude and longitude

    Inputs:
        - gdf_dataframe: a GeoDataframe with the community polygons
        - lat, lon: latitude and longitude of the Point selected
    Returns:
        - community: details of the community that contains the Point
    """
    # Convert lat and lon into a Point
    point = Point(lon, lat)
    for _, community in gdf_dataframe.iterrows():
        # Locate Point in community polygon
        if community.geometry.contains(point):
            return community
    return None


def get_community_from_name(gdf_dataframe, name):
    """
    Obtains the community details based on name

    Inputs:
        - gdf_dataframe: a GeoDataframe with the community polygons
        - name: name of the community
    Returns:
        - community: community details
    """
    for _, community in gdf_dataframe.iterrows():
        if community.GEOG == name:
            return community
    return None


def get_livability_scores(dataframe, zip_code):
    """
    Based on a zip code, returns the livability scores

    Inputs:
        - dataframe: livability index dataframe
        - zip_code: Zip code from listing selected
    Returns:
        - scores_data: dictionary with categories and scores
    """
    # Filter data
    scores = dataframe[dataframe["zip_code"] == zip_code]
    # Save into dictionary
    scores_data = {
        "Proximity": scores["score_prox"].values[0],
        "Engagement": scores["score_engage"].values[0],
        "Environment": scores["score_env"].values[0],
        "Health": scores["score_health"].values[0],
        "Housing": scores["score_house"].values[0],
        "Opportunity": scores["score_opp"].values[0],
        "Transportation": scores["score_trans"].values[0],
    }
    return scores_data


def calculate_rent(annual_income, share_on_rent):
    """
    Computes the maximum amount the user is willing to spend on rent

    Inputs:
        - annual_income: The annual income of the user
        - share_on_rent: The % the user is willing to spend on rent
    Returns:
        - maximum rent
    """
    if not annual_income:
        return 0
    elif not share_on_rent:
        return annual_income
    else:
        return annual_income * share_on_rent / 100 / 12
