from cmap import comms_with_polys, comm_id_features
from shapely.geometry import mapping
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

# Cargar datos de ArcGIS
geojson = {"type": "FeatureCollection",
           "features": []}

id = 1
for comms in comms_with_polys:
    comm_dict = {"type": "Feature",
                "id" : id,
                "geometry" : mapping(comms["comm_poly"]),
                "properties" : comms}
    del comm_dict["properties"]["comm_poly"]
    geojson["features"].append(comm_dict)
    id += 1

# Crear DataFrame
df = pd.DataFrame(comms_with_polys)

# Crear figura en Plotly Express
fig = px.choropleth(df, 
                    geojson=geojson, 
                    color="median_rent",
                    locations="GEOG",  
                    featureidkey="properties.GEOG",  
                    projection="mercator",
                    hover_data=["TOT_POP", ])

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Inicializar app Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Mapa de Median Rent por Comunidad", style={'textAlign': 'center'}),
    dcc.Graph(id="choropleth-map", figure=fig)  # Muestra el mapa generado en Plotly
])

if __name__ == "__main__":
    app.run_server(debug=True)
