import os
import webbrowser
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Construct the CSV file path using os.path.join
csv_file = os.path.join("..", "extracted_data", "Zillow-complete.csv")

# Load the CSV file (assumes it contains only Chicago data)
df = pd.read_csv(csv_file)

# Convert price columns and other key columns to numeric
df["price"] = pd.to_numeric(df["price"], errors='coerce')
df["clean_price"] = pd.to_numeric(df["clean_price"], errors='coerce')
df["livingarea"] = pd.to_numeric(df["livingarea"], errors='coerce')
df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors='coerce')
df["bathrooms"] = pd.to_numeric(df["bathrooms"], errors='coerce')

# Create a formatted price column for display using the 'price' column.
df["price_formatted"] = df["clean_price"].apply(
    lambda x: "${:,.0f}".format(x) if pd.notnull(x) else "N/A"
)

# Create a display column for bedrooms that shows "Studio" if bedrooms == 0.
df["bedrooms_display"] = df["bedrooms"].apply(
    lambda x: "Studio" if x == 0 else int(x) if pd.notnull(x) else "N/A"
)

# Define the latitude and longitude column names (adjust if needed)
lat_col = "latitude"
lon_col = "longitude"

# Helper function to create the map figure based on a filtered DataFrame.
def create_figure(filtered_df):
    fig = px.scatter_map(
        filtered_df,
        lat=lat_col,
        lon=lon_col,
        # Hover data now uses the formatted price column (price_formatted)
        hover_data=[
            "address",
            "price_formatted",
            "bedrooms_display",
            "bathrooms",
            "detailUrl"
        ],
        zoom=11,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# Create the default figure using all listings.
default_fig = create_figure(df)

# Set up the Dash app layout.
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Chicago Zillow Data Map"),
    html.Div([
        html.Label("Enter maximum rent:"),
        dcc.Input(
            id="rent-input", 
            type="number", 
            placeholder="Maximum rent", 
            value=3000  # default value; adjust as needed
        )
    ], style={'padding': '10px', 'fontSize': '20px'}),
    dcc.Graph(id="chicago-map", figure=default_fig)
])

# Callback: update the map based on user input for maximum rent.
@app.callback(
    Output("chicago-map", "figure"),
    Input("rent-input", "value")
)
def update_map(max_rent):
    # If no maximum rent is provided, show all listings.
    if max_rent is None:
        filtered_df = df
    else:
        # Use the "clean_price" column for filtering.
        filtered_df = df[df["clean_price"] <= max_rent]
    return create_figure(filtered_df)

if __name__ == '__main__':
    port = 8050
    url = f"http://127.0.0.1:{port}/"
    print(f"Running on {url}")
    webbrowser.open(url, new=2)
    app.run_server(debug=True, port=port)
