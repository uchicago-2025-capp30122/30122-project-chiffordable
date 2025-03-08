import webbrowser
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import dash_bootstrap_components as dbc

from Utils_app import get_community_from_point, get_community_from_name, get_livability_scores
from visualizations import df_listings, df_communities, df_livability, create_combined_figure, age_figure, race_figure, livability_figure

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
app.title = "CHI-ffordable"

# Define layout
app.layout = dbc.Container([
    dcc.Tabs(id="tabs", value="landing", children=[
        dcc.Tab(label="Home", value="landing"),
        dcc.Tab(label="Explore", value="visualizations"),
        dcc.Tab(label="About", value="considerations"),
    ]),
    html.Div(id='tabs-content')
],
fluid=True)

# Landing Page Layout
landing_page = html.Div([
    html.H1("CHI-ffordable"),
    html.P("[Abstract goes here]"),
    html.H3("How to use this tool"),
    html.P("[Instructions go here]")
])
# Visualization Page Layout
visualizations_page = html.Div([
    html.H1("CHI-ffordable"),
    dbc.Row([
        dbc.Col([
            html.Label("My annual income is:"),
            dcc.Input(id="rent-input", type="number", placeholder="Annual income", value=50000)
        ], width=4),
    ]),
        dbc.Row([
        dbc.Col([
            html.Label("I want to spend (%) of my income:"),
            dcc.Input(id="share-rent", type="number", placeholder="Share on rent", value=30)
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
    html.P("[List data sources here]"),
    html.H3("GitHub Repository"),
    html.A("[Link to repository]", href="#", target="_blank"),
    html.H3("Authors & Acknowledgements"),
    html.P("[Author names and acknowledgements here]")
])

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

# Visualization Page Callbacks
@app.callback(
    Output("chicago-map", "figure"),
    Input("rent-input", "value"),
    Input("share-rent", "value"),
    suppress_callback_exceptions=True
)
def update_map(annual_income, share_on_rent):
    return create_combined_figure(annual_income, share_on_rent)

@app.callback(
    Output("community-info", "children"),
    Input("chicago-map", "clickData"),
    suppress_callback_exceptions=True
)
def display_info(clickData):
    if clickData and "points" in clickData:
        selected_point = clickData["points"][0]
        if "lat" in selected_point and "lon" in selected_point:
            lat, lon = selected_point.get("lat"), selected_point.get("lon")
            listing = df_listings[(df_listings["latitude"] == lat) & (df_listings["longitude"] == lon)]
            zip_code = listing["zipcode"].values[0]
            livability = get_livability_scores(df_livability, zip_code)
            community = get_community_from_point(df_communities, lat, lon)
            community_name = community["GEOG"]
            zillow_url = listing["detailUrl"].values[0]  # Extract the Zillow link
        elif "location" in selected_point:
            community_name = selected_point.get("location")
            community = get_community_from_name(df_communities, community_name)
            livability = None
        if community is not None:
            age_data = pd.DataFrame({
                "Age Group": ["<5","5-19", "20-34", "35-49", "50-64", "65-74", "75-84", "85<"],
                "Percentage": [community["UND5"], community["A5_19"], community["A20_34"], community["A35_49"], 
                               community["A50_64"], community["A65_74"], community["A75_84"],community["OV85"]]
            })
            race_data = pd.DataFrame({
                "Race": ["White", "Hispanic", "Black", "Asian", "Other"],
                "Percentage": [community["WHITE"], community["HISP"], community["BLACK"], community["ASIAN"], community["OTHER"]]
            })
            if livability is not None:
                livability_data = pd.DataFrame({
                    "Category": ["Proximity", "Engagement", "Environment", "Health", "Housing", "Opportunity", "Transportation"],
                    "Score": [livability["Proximity"], livability["Engagement"], livability["Environment"],
                            livability["Health"], livability["Housing"], livability["Opportunity"], livability["Transportation"]]
                })
                return html.Div([
                    html.H3(f"{community_name}"),
                    html.H4(f"Median Rent: ${community['median_rent']:,.0f}"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=age_figure(age_data)), width=4),
                        dbc.Col(dcc.Graph(figure=race_figure(race_data)), width=4),
                        dbc.Col(dcc.Graph(figure=livability_figure(livability_data)), width=4),
                    ]),
                    html.Br(),
                    html.A("View Listing details", href=zillow_url, target="_blank", style={"font-size": "16px", "color": "blue"}),
                ])
            return html.Div([
                    html.H3(f"{community_name}"),
                    html.H4(f"Median Rent: ${community['median_rent']:,.0f}"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=age_figure(age_data)), width=4),
                        dbc.Col(dcc.Graph(figure=race_figure(race_data)), width=4),
                    ]),
                ])
    return "Click on a community or listing to view details."

if __name__ == '__main__':
    port = 8050
    url = f"http://127.0.0.1:{port}/"
    print(f"Running on {url}")
    webbrowser.open(url, new=2)
    app.run_server(debug=True, port=port)
