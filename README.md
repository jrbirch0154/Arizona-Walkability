# Arizona Walkability Calculator

A Python script that maps walkability value across Arizona zip codes by combining Walk Score data with Census rent data into a composite affordability-walkability index. For a quick look at the result, download and open the .html file.

## What It Does

The script pulls median rent figures from the Census ACS API and merges them with cached Walk Score data for every Arizona ZCTA (zip code tabulation area). It then ranks each zip code on both walkability and affordability, combines them into a single composite score, and renders an interactive choropleth map with Plotly.

The output is a standalone HTML file (`walkscore_chart.html`) with a dropdown that lets you toggle between the composite score, raw walk score, and median rent.

## Requirements

```
pandas
geopandas
plotly
requests
python-dotenv
```

Install with:

```bash
pip install pandas geopandas plotly requests python-dotenv
```

## Setup

### 1. Census API Key

Get a free key at [api.census.gov](https://api.census.gov/). Add it to a `.env` file:

```
KEY=your_census_api_key_here
```

### 2. Walk Score API Key (for refreshing data)

A Walk Score API key is needed only if you want to re-fetch scores. Add it to `.env`:

```
WALK_KEY=your_walkscore_api_key_here
```

The Walk Score fetch block is commented out by default. The repo uses `walkscore_cache.csv` so you do not have to call the API repeatedly.

### 3. Shapefile

Download the 2022 ZCTA shapefile from the Census Bureau:

[https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/](https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/)

Extract it and place `tl_2022_us_zcta520.shp` (and its companion files) in the project directory.

## Usage

```bash
python walkability_calculator.py
```

This will open the map in your browser and save `walkscore_chart.html` to the project directory.

## Data Sources

| Data | Source |
|---|---|
| Median gross rent (B25064) | Census ACS 5-Year Estimates, 2023 |
| Walk Score / Transit Score / Bike Score | Walk Score API (cached in `walkscore_cache.csv`) |
| ZCTA boundaries | Census TIGER/Line Shapefiles, 2022 |

## Scoring Methodology

Zip codes are scored on two dimensions, each converted to a percentile rank:

- **Walk rank:** percentile rank of raw Walk Score
- **Affordability rank:** percentile rank of `1 / median_rent` (lower rent = higher rank)

The composite score is the average of the two ranks, ranging from 0 to 1. A higher score means a zip code is both more walkable and more affordable relative to other Arizona ZCTAs.

## File Structure

```
.
├── walkability_calculator.py
├── walkscore_cache.csv       # cached Walk Score API results
├── tl_2022_us_zcta520.shp    # Census ZCTA shapefile (download separately)
├── tl_2022_us_zcta520.*      # shapefile companion files
├── .env                      # API keys (not committed)
└── walkscore_chart.html      # output map
```

## Notes

- The script filters to ZCTAs in the range `85000` to `86599`, which covers Arizona.
- Zip codes with suppressed or null rent values are dropped.
- The Walk Score API has rate limits; the commented-out fetch loop includes a 0.1-second delay between requests.

## Author

Jacob Birch
