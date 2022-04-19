import pandas as pd
import numpy as np
import re

from geopy import Nominatim

# Pub Core Data

# import raw pub core data
df = pd.read_csv("/content/raw-london-pubs.csv", index_col=[0])
print(df.head())

# drop duplicated rows of core pub dataframe
print(df.duplicated().value_counts())
df = df.drop_duplicates()
print(df.shape)

# extract selected data from column with values in dictionaries
def extract_value(df, column, regex):
    return df[column].str.extract(regex)


df["geocodes"] = extract_value(df, "geocodes", "{'main':.\{(.*?)\}")
df["address"] = extract_value(df, "location", "{'address':.'(.*?)',")
df["locality"] = extract_value(df, "location", "'locality':.'(.*?)',")
df["neighborhood"] = extract_value(df, "location", "'neighborhood':.\['(.*)'\]")
df["postcode"] = extract_value(df, "location", "'postcode':.'(.*?)'")
df["category"] = extract_value(df, "categories", "'name':.'(.*?)'")

print(df.head())

# check for null values in geocodes column
print(df.info())
df["geocodes"].isnull().sum()
empty_geocodes = df[df["geocodes"].isnull()]

# get coordinate to fill the null values in the geocodes column
geolocator = Nominatim(user_agent="women_safety")


def get_geocodes():
    for col, row in empty_geocodes.iterrows():
        get_geocodes_by_street(row)


# try to find coordinates from addres
def get_geocodes_by_street(row):
    address = row["address"]
    try:
        location = geolocator.geocode(f"{address}, London")
        row[
            "geocodes"
        ] = f"'latitude': {location.latitude}, 'longitude': {location.longitude}"
    except:
        get_geocodes_by_postcode(row)


# try to find coordinates from postcode
def get_geocodes_by_postcode(row):
    id = row["fsq_id"]
    try:
        location = geolocator.geocode(row["postcode"])
        row[
            "geocodes"
        ] = f"'latitude': {location.latitude}, 'longitude': {location.longitude}"
    except:
        row["geocodes"] = np.nan
        print(f"It was not possible to find coordinates for {id}")


# get missing geocodes using geopy library
get_geocodes()

# check for missing data
print(empty_geocodes["geocodes"].isnull().sum())

# assign the geocodes found to the main dataframe
df["geocodes"][df["geocodes"].isnull()] = empty_geocodes["geocodes"]
print(df["geocodes"].isnull().sum())

# divide the geocode column into two new columns: latitude and longitude
def get_lat_long(df):
    lat_list = []
    long_list = []
    geocodes_split = df["geocodes"].str.split(",")
    for lat, longi in geocodes_split:
        lat = re.search("latitude':.(.*)", lat).group(1)
        lat_list.append(lat)
        longi = re.search("longitude':.(.*)", longi).group(1)
        long_list.append(longi)
    df["latitude"] = lat_list
    df["longitude"] = long_list


get_lat_long(df)

print(df.head())

# copy the changed dataframe
pubs_data = df.copy()

# drop columns that will not be use in this project
pubs_data = pubs_data.drop(columns=["categories", "geocodes", "location"], axis=1)
print(pubs_data.head())

# save updated pubs dataframe into csv
pubs_data.to_csv("data-wrangling-pubs-data-clean.csv")


# Pub Rich Data

# import pubs detailed data dataframe
pubs_rich = pd.read_csv("/content/raw-london-pubs-detailed-data.csv", index_col=[0])
print(pubs_rich.head())
print(pubs_rich.info())

# check for duplicates and drop them
pubs_rich.duplicated().value_counts()
pubs_rich = pubs_rich.drop_duplicates()

# merge the pubs updated dataframe with the pubs detailed data dataframe
print(pubs_data.shape)
print(pubs_rich.shape)
pubs_df = df.merge(pubs_rich, how="left", on="fsq_id")

print(pubs_df.info())
print(pubs_df.head())

# copy the new dataframe
pubs_full = pubs_df.copy()

# drop columns that will not be use in this project
pubs_full = pubs_full.drop(columns=["categories", "geocodes", "location"])
print(pubs_full.head())

# save updated dataframe into csv
pubs_full.to_csv("data-wrangling-pubs-full-clean.csv")
