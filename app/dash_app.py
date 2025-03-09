import webbrowser
import random
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import dash_bootstrap_components as dbc

from Utils_app import get_community_from_point, get_community_from_name, get_livability_scores
from Utils_app import abstract_str, instructions_str, data_sources_str, repo_str, authors_str
from visualizations import df_listings, df_communities, df_livability
from visualizations import create_combined_figure, age_figure, race_figure, livability_figure

# ---------------------------- Init App ---------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], 
                suppress_callback_exceptions=True)
app.title = "CHI-ffordable"

# ---------------------------- Define Layout ----------------------------------
app.layout = dbc.Container([
    dcc.Tabs(id="tabs", value="landing", children=[
        dcc.Tab(label="Home", value="landing"),
        dcc.Tab(label="Explore", value="visualizations"),
        dcc.Tab(label="About", value="considerations"),
    ]),
    html.Div(id='tabs-content')
],
fluid=True)

# Home Page Layout
landing_page = html.Div([
    html.H1("CHI-ffordable"),
    html.P(abstract_str),
    html.H3("How to use this tool"),
    html.P(instructions_str)
])
# Visualization Page Layout
visualizations_page = html.Div([
    html.H1("CHI-ffordable"),
    dbc.Row([
        dbc.Col([
            html.Label("My annual income is:"),
            dcc.Input(id="rent-input", 
                      type="number", 
                      placeholder="Annual income", 
                      value=50000)  # Initial value set to $50,000
        ], width=4),
    ]),
        dbc.Row([
        dbc.Col([
            html.Label("I want to spend (%) of my income on rent:"),
            dcc.Input(id="share-rent", 
                      type="number",
                      min = 0,
                      max = 100, 
                      placeholder="Share on rent", 
                      value=30) # Initial value set to 30%
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="chicago-map"), width=4),
        dbc.Col(html.Div(id="community-info"), width=8),
    ])
])

# Considerations Page Layout
considerations_page = html.Div([
    html.H1("Considerations"),
    html.H3("Data Sources"),
    html.P(data_sources_str),
    html.H3("GitHub Repository"),
    html.A(repo_str, href="#", target="_blank"),
    html.H3("Authors & Acknowledgements"),
    html.P(authors_str)
])
# ---------------------------- App Callbacks ----------------------------------
# Update page content based on selected tab
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    suppress_callback_exceptions=True
)
def update_tab(tab_name):
    if tab_name == "landing":
        return landing_page
    elif tab_name == "visualizations":
        return visualizations_page
    elif tab_name == "considerations":
        return considerations_page

# Visualization Page Callbacks: rent-input and share-rent
@app.callback(
    Output("chicago-map", "figure"),
    Input("rent-input", "value"),
    Input("share-rent", "value"),
    suppress_callback_exceptions=True
)
# Based on callbacks, update map
def update_map(annual_income, share_on_rent):
    return create_combined_figure(annual_income, share_on_rent)

# Visualization Page Callback: clickData
@app.callback(
    Output("community-info", "children"),
    Input("chicago-map", "clickData"),
    suppress_callback_exceptions=True
)
def display_info(clickData):
    # Case 1: User clicks a listing Point
    if clickData and "points" in clickData:
        # Fetch (1)community-level and (2)livability data 
        # based on lat, lon, zip_code
        selected_point = clickData["points"][0]
        if "lat" in selected_point and "lon" in selected_point:
            lat, lon = selected_point.get("lat"), selected_point.get("lon")
            listing = df_listings[(df_listings["latitude"] == lat) & 
                                  (df_listings["longitude"] == lon)]
            zip_code = listing["zipcode"].values[0]
            livability = get_livability_scores(df_livability, zip_code) # (2)
            community = get_community_from_point(df_communities, lat, lon) # (1)
            community_name = community["GEOG"]
            zillow_url = listing["detailUrl"].values[0]  # Extract Zillow link
        # Case 1: User clicks a community
        elif "location" in selected_point:
            # Extract community-level data based on community name
            # Note: No livability data available, because community-zip_code 
            # incompatibility
            community_name = selected_point.get("location")
            community = get_community_from_name(df_communities, community_name)
            livability = None
        if community is not None:
            # Create age_data for Age Distribution bar graph
            age_data = pd.DataFrame({
                "Age Group": ["<5","5-19", "20-34", "35-49", "50-64", "65-74", 
                              "75-84", "85<"],
                "Percentage": [community["UND5"], community["A5_19"], 
                               community["A20_34"], community["A35_49"], 
                               community["A50_64"], community["A65_74"], 
                               community["A75_84"],community["OV85"]]
            })
            # Create race_data for Racial Composition bar graph
            race_data = pd.DataFrame({
                "Race": ["White", "Hispanic", "Black", "Asian", "Other"],
                "Percentage": [community["WHITE"], community["HISP"], 
                               community["BLACK"], community["ASIAN"], 
                               community["OTHER"]]
            })
            # If livability data is available,
            if livability is not None:
                # Create livability_data for Livability scores bar graph
                livability_data = pd.DataFrame({
                    "Category": ["Proximity", "Engagement", "Environment", 
                                 "Health", "Housing", "Opportunity", 
                                 "Transportation"],
                    "Score": [livability["Proximity"], livability["Engagement"], 
                              livability["Environment"], livability["Health"], 
                              livability["Housing"], livability["Opportunity"], 
                              livability["Transportation"]]
                })
                # Page layout if livability data is available
                return html.Div([
                    html.H3(f"{community_name}"),
                    html.H4(f"Median Rent: ${community['median_rent']:,.0f}"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=age_figure(age_data)), 
                                width=4),
                        dbc.Col(dcc.Graph(figure=race_figure(race_data)), 
                                width=4),
                        dbc.Col(dcc.Graph(figure=livability_figure(livability_data)), 
                                width=4),
                    ]),
                    html.Br(),
                    html.A("View Listing details", 
                           href=zillow_url, 
                           target="_blank", 
                           style={"font-size": "16px", "color": "blue"}),
                ])
            # Page layout if livability data is NOT available
            return html.Div([
                    html.H3(f"{community_name}"),
                    html.H4(f"Median Rent: ${community['median_rent']:,.0f}"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=age_figure(age_data)), 
                                width=4),
                        dbc.Col(dcc.Graph(figure=race_figure(race_data)), 
                                width=4),
                    ]),
                ])
    # when there is NOT clickData (nothing has been selected), show instructions
    return "Click on a community or listing to view details."

# Run application on web browser
if __name__ == '__main__':
    port = 8052
    url = f"http://127.0.0.1:{port}/"
    print(f"Running on {url}")
    webbrowser.open(url, new=2)
    app.run_server(debug=True, port=port)
