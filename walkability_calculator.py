# Walkability Calculator
# Tue Apr 21 18:30:28 2026
# Jacob Birch

# %% Initializing

import pandas as pd
import requests
import geopandas as gpd
import plotly.express as px
import plotly.io as pio
import json
from dotenv import load_dotenv
import os

load_dotenv()

pio.renderers.default = "browser"

gdf = gpd.read_file("tl_2022_us_zcta520.shp")
# this comes from https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/

# Filter to Arizona ZCTAs and get centroids
gdf = gdf.rename(columns={"ZCTA5CE20": "zcta"})
gdf = gdf[gdf["zcta"].between("85000", "86599")]
gdf["centroid"] = gdf.geometry.centroid
gdf["lat"] = gdf["centroid"].y
gdf["lon"] = gdf["centroid"].x


KEY = os.getenv("KEY")  # for census API
# api.census.gov/data/2023/acs/acs5/variables.html

params = {
    "get": "NAME,B25064_001E",
    "for": "zip code tabulation area:*",
    # "in": "state:04"
    "key": KEY,
}

r = requests.get("https://api.census.gov/data/2023/acs/acs5", params=params)

# %% DF
data = r.json()
df = pd.DataFrame(data[1:], columns=data[0])
df = df.rename(
    columns={"B25064_001E": "median_rent", "zip code tabulation area": "zcta"}
)
df["median_rent"] = pd.to_numeric(df["median_rent"])
df = df[df["median_rent"] > 0]  # drop null/suppressed values
df = df[df["zcta"].between("85000", "86599")]
df = df.merge(gdf[["zcta", "lat", "lon", "geometry"]], on="zcta")

# %% Walk score
# =============================================================================
#
# import time
#
# WALK_KEY= os.getenv("WALK_KEY")
#
# def get_walkscore(lat, lon, address=""):
#     r = requests.get(
#         "https://api.walkscore.com/score",
#         params={
#             "format": "json",
#             "lat": lat,
#             "lon": lon,
#             "address": address,
#             "wsapikey": WALK_KEY
#         }
#     )
#     data = r.json()
#     return data.get("walkscore"), data.get("transit", {}).get("score"), data.get("bike", {}).get("score")
#
# results = []
# for _, row in df.iterrows():
#     walk, transit, bike = get_walkscore(row["lat"], row["lon"])
#     results.append({"zcta": row["zcta"], "walk_score": walk, "transit_score": transit, "bike_score": bike})
#     time.sleep(0.1)
#
# scores_df = pd.DataFrame(results)
# scores_df.to_csv("walkscore_cache.csv",index=False)
# =============================================================================

scores_df = pd.read_csv("walkscore_cache.csv")
# I saved it to a cache so I don't have to make this call over and over
df["zcta"] = pd.to_numeric(df["zcta"])
df = df.merge(scores_df, on="zcta")


# %% Math Work

# df['walkrent_value'] = df['walk_score'] / df['median_rent'] # works, but not the best

df["walk_rank"] = df["walk_score"].rank(pct=True)  # normalize it
df["afford_rank"] = (1 / df["median_rent"]).rank(pct=True)
df["composite_score"] = (df["walk_rank"] + df["afford_rank"]) / 2

# %% Map it
df_map = df[
    ["zcta", "composite_score", "geometry", "median_rent", "walk_score"]
].copy()
gdf_map = gpd.GeoDataFrame(df_map, geometry="geometry")

geojson = json.loads(gdf_map.to_json())

metrics = {
    "Composite Score": "composite_score",
    "Walk Score": "walk_score",
    "Median Rent": "median_rent",
}

fig = px.choropleth_map(
    df,
    geojson=geojson,
    locations="zcta",
    featureidkey="properties.zcta",
    color="composite_score",
    hover_data={
        "zcta": True,
        "walk_score": True,
        "median_rent": True,
        "composite_score": ":.3f",
    },
    color_continuous_scale="RdYlGn",
    map_style="carto-positron",
    zoom=6,
    center={"lat": 33.5, "lon": -112.0},
    opacity=0.7,
    title="Arizona Walkability Value by ZCTA",
)

fig.update_layout(
    updatemenus=[
        {
            "buttons": [
                {
                    "label": label,
                    "method": "update",
                    "args": [
                        {"z": [df[col].tolist()]},
                        {"title": f"Arizona - {label}"},
                    ],
                }
                for label, col in metrics.items()
            ],
            "direction": "down",
            "showactive": True,
            "x": 0.1,
            "y": 1.1,
        }
    ],
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
)

fig.show()

fig.write_html("walkscore_chart.html")
print("walkscore_chart.html saved")
