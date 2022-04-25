import pandas as pd
import requests
import re
import time

from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


# Web Scraping for London Boroughs

response = requests.get("https://directory.londoncouncils.gov.uk/")

soup = BeautifulSoup(response.text, "html.parser")
london_table = soup.find("table", {"class": "table"})

london_df = pd.read_html(str(london_table))
london_df = pd.DataFrame(london_df[0])

print(london_df.head())

london_df.rename(columns={"Authority": "borough"}, inplace=True)

print(london_df["borough"].unique())

london_df[
    (london_df["borough"] != "City of London Corporation")
    & (london_df["borough"] != "City of Westminster")
] = london_df["borough"].str.extract("^.B.(.*)")

london_df[london_df["borough"] == "City of London Corporation"] = "City of London"

london_boroughs = london_df["borough"].tolist()
print(london_boroughs)

# get latitude and longitude for each listed borough
geolocator = Nominatim(user_agent="women_safety")


def get_geocodes(neighborhood_list):
    coordinates_dict = {}
    for neighborhood in neighborhood_list:
        location = geolocator.geocode(f"{neighborhood}, London")
        if hasattr(location, "latitude"):
            coordinates_dict[neighborhood] = f"{location.latitude},{location.longitude}"
        else:
            coordinates_dict[neighborhood] = None
    return coordinates_dict


coordinates = get_geocodes(london_boroughs)

# Collecting pubs data from Foursquare API

pubs_category = "13018"
police_category = "12072"

# make request to fetch venues data from Foursquare API
def make_request(url):
    headers = {"Accept": "application/json", "Authorization": "password"}
    response = requests.request("GET", url, headers=headers)
    return response


# get next url from Foursquare API response
def get_next_url(response):
    try:
        return re.findall("<(.*?)>", response.headers["Link"])[0]
    except (KeyError, IndexError):
        return None


# get venues data from a given coordinate for the given categories
def get_nearby_venues_data(coordinate, categories):
    json_list = []
    url = f"https://api.foursquare.com/v3/places/search?ll={coordinate}&radius=500&categories={categories}&fields=fsq_id%2Cname%2Cgeocodes%2Clocation%2Ccategories&limit=50"

    while url != None:
        response = make_request(url)
        json_file = response.json()
        json_list.append(json_file)

        url = get_next_url(response)
        time.sleep(0.1)
        print(url)
        print(response.headers)

    return json_list


# get venues data of given categories for all the coordinates of London's neighborhoods
def get_venues_data(categories):
    venues_data = []
    for coordinate in coordinates.values():
        nearby_venues = get_nearby_venues_data(coordinate, categories)
        venues_data.extend(nearby_venues)
    return venues_data


# collecting Pubs data
pubs_venues_data = get_venues_data(pubs_category)
print(len(pubs_venues_data))

# return flattened list of venues data results
def parse_json_list(raw_venues_data):
    list_venues = []
    for json in raw_venues_data[1:]:
        if "results" in json:
            list_venues.extend(json["results"])
        else:
            continue
    return list_venues


# transform flattened list of pubs venues data into pandas dataframe
list_pubs = parse_json_list(pubs_venues_data)
print(len(list_pubs))
df = pd.DataFrame(list_pubs)

print(df.head())

# check for duplicated venues data
print(df.fsq_id.duplicated().value_counts())

# save dataframe into csv file
df.to_csv("raw-london-pubs.csv")


# Collecting Subway and Police Data from Foursquare API

# collecting Police and Metro data
police_data = get_venues_data(police_category)
print(len(police_data))

# transform flattened list of police and metro venues data into pandas dataframe
police_json = parse_json_list(police_data)
print(len(police_json))
df2 = pd.DataFrame(police_json)
print(df2.head())

# check for duplicated venues data
print(df2.fsq_id.duplicated().value_counts())

# save dataframe into csv file
df2.to_csv("raw-london-police-station-data.csv")


# Venues detailed data from Foursquare API

# get rating, popularity and price range data of given venues from Foursquare API
def get_detailed_data(dataframe):
    json_list = []
    for id in dataframe.fsq_id:
        url = f"https://api.foursquare.com/v3/places/{id}?fields=fsq_id%2Crating%2Cpopularity%2Cprice"

        headers = {"Accept": "application/json", "Authorization": "password"}

        response = requests.request("GET", url, headers=headers)
        json_file = response.json()
        json_list.append(json_file)
        print(response.text)
    return json_list


# collection pubs detailed data
json_list = get_detailed_data(df)
print(len(json_list))

# return flattened list of venues detailed data
list_of_venues = []
for json in json_list:
    list_of_venues.append(json)

print(list_of_venues)

# transform flattened list of pubs detailed data into pandas dataframe
df3 = pd.DataFrame(list_of_venues)
print(df3.head())

# save dataframe into csv file
df3.to_csv("raw-london-pubs-detailed-data.csv")
