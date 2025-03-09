import os
import webbrowser
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import geopandas as gpd
from shapely import wkt
import plotly.express as px
import sys

# Load listings data
csv_file = os.path.join("extracted_data", "Zillow.csv")
df_listings = pd.read_csv(csv_file)
df_listings["clean_price"] = pd.to_numeric(df_listings["clean_price"], errors="coerce")
df_listings["latitude"] = pd.to_numeric(df_listings["latitude"], errors="coerce")
df_listings["longitude"] = pd.to_numeric(df_listings["longitude"], errors="coerce")

# Load communities data
sys.path.append("./extracting")
from cmap import csv_format  # Importing external data

df_communities = pd.DataFrame(csv_format)
df_communities["geometry"] = df_communities["comm_poly"].apply(
    lambda x: wkt.loads(x) if isinstance(x, str) else x
)
gdf_communities = gpd.GeoDataFrame(df_communities, geometry="geometry")


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


app = dash.Dash(__name__)
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
        community_name = selected_point.get("location")
        if community_name:
            community_data = gdf_communities[gdf_communities["GEOG"] == community_name]
            if not community_data.empty:
                info = community_data.iloc[0]
                table_data = {
                    "Community characteristics": [
                        "Median Rent",
                        "Age 5-19 (%)",
                        "Age 20-34 (%)",
                        "Age 35-49 (%)",
                        "Age 50-64 (%)",
                        "Age 65-74 (%)",
                        "Age 75+ (%)",
                        "White (%)",
                        "Hispanic (%)",
                        "Black (%)",
                        "Asian (%)",
                    ],
                    " ": [
                        info["median_rent"],
                        info["A5_19"],
                        info["A20_34"],
                        info["A35_49"],
                        info["A50_64"],
                        info["A65_74"],
                        info["A75_84"],
                        info["WHITE"],
                        info["HISP"],
                        info["BLACK"],
                        info["ASIAN"],
                    ],
                }
                return dash_table.DataTable(
                    columns=[{"name": col, "id": col} for col in table_data.keys()],
                    data=pd.DataFrame(table_data).to_dict("records"),
                    style_table={"overflowX": "auto"},
                )
    return "Click on a community to view details."


if __name__ == "__main__":
    port = 8050
    url = f"http://127.0.0.1:{port}/"
    print(f"Running on {url}")
    webbrowser.open(url, new=2)
    app.run_server(debug=True, port=port)
