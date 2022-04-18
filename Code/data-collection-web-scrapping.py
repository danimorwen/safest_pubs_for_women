import requests
import pandas as pd

from bs4 import BeautifulSoup

# get data from Wiki Open Street Map page about London Underground
response = requests.get(
    "https://wiki.openstreetmap.org/wiki/List_of_London_Underground_stations"
)
soup = BeautifulSoup(response.text, "html.parser")

# select the first table in the webpage
underground_table = soup.find("table", {"class": "wikitable"})

# transform table into a pandas dataframe
underground_df = pd.read_html(str(underground_table))
underground_df = pd.DataFrame(underground_df[0])
print(underground_df.head())

# check columns names
print(underground_df.columns.tolist())

# drop columns that will not be use in this project
underground_df = underground_df.drop(
    ["Platform / Entrance", "Collected By", "Collected On", "Step free"], axis=1
)
print(underground_df.head())

# rename columns name to lower case
underground_df.rename(
    {"Name": "name", "Latitude": "latitude", "Longitude": "longitude", "Line": "line"},
    axis=1,
    inplace=True,
)
print(underground_df.head())

# Find row without latitude correct data and assign the first value
underground_df[underground_df["latitude"] == "51.49787 +/- 0.000011 (from 3 readings)"]
underground_df.loc[43, ["latitude", "longitude"]] = ["51.49787", "-0.04967"]
print(underground_df.loc[43])

# transform the data in the latitude and longitude columns into numerical type
pd.to_numeric(underground_df["latitude"])
pd.to_numeric(underground_df["longitude"])

# save the dataframe into csv file
underground_df.to_csv("london_underground.csv")
