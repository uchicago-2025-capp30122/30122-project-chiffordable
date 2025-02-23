import os
import webbrowser
import dash
from dash import dcc, html  # Dash 2.0+ style
import pandas as pd
import plotly.express as px

# Construct the CSV file path using os.path.join
csv_file = os.path.join("..", "extracted_data", "Zillow-complete.csv")

# Load the CSV file (assumes it contains only Chicago data)
df = pd.read_csv(csv_file)

# Create new columns for hover information:
# Format the clean_price as currency (e.g., "$1,234")
df["clean_price_formatted"] = df["clean_price"].apply(
    lambda x: "${:,.0f}".format(x) if pd.notnull(x) else "N/A"
)
# For bedrooms, if the value is 0, display "Studio" instead of 0.
df["bedrooms_display"] = df["bedrooms"].apply(
    lambda x: "Studio" if x == 0 else x
)

# Specify the column names for latitude and longitude
lat_col = "latitude"   # Adjust if necessary
lon_col = "longitude"  # Adjust if necessary

# Create a scatter map using Plotly Express.
# The hover_data now shows address, formatted clean price, living area,
# bedrooms (with "Studio" for 0), bathrooms, and the detail URL.
fig = px.scatter_map(
    df,
    lat=lat_col,
    lon=lon_col,
    hover_data=[
        "address",
        "clean_price_formatted",
        "bedrooms_display",
        "bathrooms",
        "detailUrl"
    ],
    zoom=11,       # Adjust zoom level as needed
    height=600
)

# Use an open-source map style that doesn't require a Mapbox token.
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Create the Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Chicago Zillow Data Map"),
    dcc.Graph(id="chicago-map", figure=fig)
])

if __name__ == '__main__':
    # Set the desired port and construct the URL.
    port = 8050
    url = f"http://127.0.0.1:{port}/"
    print(f"Running on {url}")
    
    # Open the default web browser to the URL.
    webbrowser.open(url, new=2)
    
    # Run the Dash server.
    app.run_server(debug=True, port=port)

