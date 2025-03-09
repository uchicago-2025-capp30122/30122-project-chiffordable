import os
import webbrowser
import dash
from dash import dcc, html, dash_table, State, callback, Patch, clientside_callback
from dash.dependencies import Input, Output
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import plotly.express as px
import sys
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url

# Load listings data
csv_file = os.path.join("extracted_data", "Zillow.csv")
df_listings = pd.read_csv(csv_file)
df_listings["clean_price"] = pd.to_numeric(df_listings["clean_price"], errors="coerce")
df_listings["latitude"] = pd.to_numeric(df_listings["latitude"], errors="coerce")
df_listings["longitude"] = pd.to_numeric(df_listings["longitude"], errors="coerce")
df_listings["zipcode"] = df_listings["zipcode"].astype(str).str.zfill(5)

# Load communities data
sys.path.append("./extracting")
from cmap import csv_format  # Importing external data

df_communities = pd.DataFrame(csv_format)
df_communities["geometry"] = df_communities["comm_poly"].apply(
    lambda x: wkt.loads(x) if isinstance(x, str) else x
)
gdf_communities = gpd.GeoDataFrame(df_communities, geometry="geometry")

# Load livability index data
livability_path = os.path.join("extracted_data", "livability_incompleted.csv")
df_livability = pd.read_csv(livability_path)
df_livability["zip_code"] = df_livability["zip_code"].astype(str).str.zfill(5)


def gdf_to_geojson(gdf):
    features = []
    for _, row in gdf.iterrows():
        feature = {
            "type": "Feature",
            "geometry": row["geometry"].__geo_interface__,
            "properties": {"GEOG": row["GEOG"], "median_rent": row["median_rent"]},
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}


def get_community_from_point(lat, lon):
    point = Point(lon, lat)
    for _, community in gdf_communities.iterrows():
        if community.geometry.contains(point):
            return community
    return None


def get_community_from_name(name):
    for _, community in gdf_communities.iterrows():
        if community.GEOG == name:
            return community
    return None


def get_livability_scores(zip_code):
    scores = df_livability[df_livability["zip_code"] == zip_code]
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


def create_combined_figure(max_rent):
    filtered_listings = df_listings[df_listings["clean_price"] <= max_rent]
    filtered_communities = gdf_communities[gdf_communities["median_rent"] <= max_rent]
    geojson_data = gdf_to_geojson(filtered_communities)

    fig = px.choropleth_map(
        filtered_communities,
        geojson=geojson_data,
        locations=filtered_communities.GEOG,
        featureidkey="properties.GEOG",
        color="median_rent",
        color_continuous_scale="Plasma",
        opacity=0.4,
        hover_name="GEOG",
        hover_data=["median_rent"],
        center={"lat": 41.8674, "lon": -87.6275},
        zoom=9.5,
        height=600,
    )

    fig.add_scattermap(
        lat=filtered_listings["latitude"],
        lon=filtered_listings["longitude"],
        mode="markers",
        marker=dict(size=6, color="grey"),
        hovertext=filtered_listings["clean_price"].apply(
            lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A"
        ),
        name="Listings",
    )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [
        html.H1("Chicago Housing & Communities Map"),
        html.Div(
            [
                html.Label("Enter maximum rent:"),
                dcc.Input(
                    id="rent-input",
                    type="number",
                    placeholder="Maximum rent",
                    value=1500,
                ),
            ],
            style={"padding": "10px", "fontSize": "20px"},
        ),
        html.Div(
            [
                dcc.Graph(id="chicago-map", figure=create_combined_figure(1500)),
                html.Div(
                    id="community-info",
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "padding": "10px",
                    },
                ),
            ],
            style={"display": "flex"},
        ),
    ]
)


@app.callback(Output("chicago-map", "figure"), Input("rent-input", "value"))
def update_map(max_rent):
    return create_combined_figure(max_rent)


@app.callback(Output("community-info", "children"), Input("chicago-map", "clickData"))
def display_info(clickData):
    if clickData and "points" in clickData:
        selected_point = clickData["points"][0]
        if "lat" in selected_point and "lon" in selected_point:
            lat, lon = selected_point.get("lat"), selected_point.get("lon")
            listing = df_listings[
                (df_listings["latitude"] == lat) & (df_listings["longitude"] == lon)
            ]
            zip_code = listing["zipcode"].values[0]
            livability = get_livability_scores(zip_code)
            community = get_community_from_point(lat, lon)
            community_name = community["GEOG"]
        elif "location" in selected_point:
            community_name = selected_point.get("location")
            community = get_community_from_name(community_name)
            livability = None
        if community is not None:
            age_data = pd.DataFrame(
                {
                    "Age Group": [
                        "<5",
                        "5-19",
                        "20-34",
                        "35-49",
                        "50-64",
                        "65-74",
                        "75-84",
                        "85<",
                    ],
                    "Percentage": [
                        community["UND5"],
                        community["A5_19"],
                        community["A20_34"],
                        community["A35_49"],
                        community["A50_64"],
                        community["A65_74"],
                        community["A75_84"],
                        community["OV85"],
                    ],
                }
            )
            race_data = pd.DataFrame(
                {
                    "Race": ["White", "Hispanic", "Black", "Asian", "Other"],
                    "Percentage": [
                        community["WHITE"],
                        community["HISP"],
                        community["BLACK"],
                        community["ASIAN"],
                        community["OTHER"],
                    ],
                }
            )
            if livability is not None:
                livability_data = pd.DataFrame(
                    {
                        "Category": [
                            "Proximity",
                            "Engagement",
                            "Environment",
                            "Health",
                            "Housing",
                            "Opportunity",
                            "Transportation",
                        ],
                        "Score": [
                            livability["Proximity"],
                            livability["Engagement"],
                            livability["Environment"],
                            livability["Health"],
                            livability["Housing"],
                            livability["Opportunity"],
                            livability["Transportation"],
                        ],
                    }
                )
                return html.Div(
                    [
                        html.H3(f"{community_name}"),
                        html.H4(f"Median Rent: ${community['median_rent']:,.0f}"),
                        dcc.Graph(
                            figure=px.bar(
                                age_data,
                                x="Age Group",
                                y="Percentage",
                                title="Age Distribution",
                            )
                        ),
                        dcc.Graph(
                            figure=px.bar(
                                race_data,
                                x="Race",
                                y="Percentage",
                                title="Racial Composition",
                            )
                        ),
                        dcc.Graph(
                            figure=px.bar(
                                livability_data,
                                x="Category",
                                y="Score",
                                title="Livability Scores",
                            )
                        ),
                    ]
                )
            return html.Div(
                [
                    html.H3(f"{community_name}"),
                    html.H4(f"Median Rent: ${community['median_rent']:,.0f}"),
                    dcc.Graph(
                        figure=px.bar(
                            age_data,
                            x="Age Group",
                            y="Percentage",
                            title="Age Distribution",
                        )
                    ),
                    dcc.Graph(
                        figure=px.bar(
                            race_data,
                            x="Race",
                            y="Percentage",
                            title="Racial Composition",
                        )
                    ),
                ]
            )
    return "Click on a community or listing to view details."


if __name__ == "__main__":
    port = 8050
    url = f"http://127.0.0.1:{port}/"
    print(f"Running on {url}")
    webbrowser.open(url, new=2)
    app.run_server(debug=True, port=port)
