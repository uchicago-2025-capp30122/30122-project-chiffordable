import os
import webbrowser
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import geopandas as gpd
from shapely import wkt
import plotly.express as px
import sys  
sys.path.append('./extracting')  # Add the folder to the Python path
from cmap import csv_format  # Now you can import

# Load the CSV file
df = pd.DataFrame(csv_format)

# Convert MultiPolygon from WKT to geometry
df['geometry'] = df['comm_poly']#.apply(wkt.loads)

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Convert GeoDataFrame to GeoJSON
geojson = gdf.__geo_interface__

# Default figure
def create_figure(gdf, threshold=None):
    # Add a color column: 'gray' if median_rent <= threshold, else 'blue'
    if threshold is not None:
        gdf['color'] = gdf['median_rent'].apply(lambda x: 'gray' if x <= threshold else 'blue')
    else:
        gdf['color'] = 'blue'

    fig = px.choropleth_map(
        gdf,
        geojson=geojson,
        locations=gdf.index,
        color="color",
        hover_name="GEOG",
        hover_data=["median_rent"],
        center={"lat": 41.8781, "lon": -87.6298},
        zoom=10,
        height=600,
        color_discrete_map={"gray": "gray", "blue": "blue"}
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

default_fig = create_figure(gdf)

# Set up the Dash app layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Chicago Community Areas Map"),
    html.Div([
        html.Label("Filter by Maximum Median Rent:"),
        dcc.Input(
            id="rent-input",
            type="number",
            placeholder="Enter maximum rent",
            style={'width': '300px', 'padding': '5px', 'fontSize': '16px'}
        )
    ], style={'padding': '10px'}),
    dcc.Graph(id="chicago-map", figure=default_fig)
])

# Callback: update the map based on rent threshold
@app.callback(
    Output("chicago-map", "figure"),
    Input("rent-input", "value")
)
def update_map(max_rent):
    if max_rent is None:
        return create_figure(gdf)
    else:
        return create_figure(gdf, threshold=max_rent)

if __name__ == '__main__':
    port = 8050
    url = f"http://127.0.0.1:{port}/"
    print(f"Running on {url}")
    webbrowser.open(url, new=2)
    app.run_server(debug=True, port=port)
