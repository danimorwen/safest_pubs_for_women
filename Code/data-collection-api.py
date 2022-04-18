import pandas as pd
import requests
import re
import time

from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

# Web Scraping for London Neighborhoods

response = requests.get(
    "https://en.wikipedia.org/wiki/List_of_areas_of_London#List_of_districts_and_neighbourhoods_of_London"
)

soup = BeautifulSoup(response.text, "html.parser")

london_table = soup.find("table", {"class": "wikitable"})

london_df = pd.read_html(str(london_table))
london_df = pd.DataFrame(london_df[0])

print(london_df.head())
print(london_df.columns.tolist())

london_df.rename(
    columns={
        "Location": "location",
        "London\xa0borough": "borough",
        "Post town": "town",
        "Postcode\xa0district": "post_code",
    },
    inplace=True,
)

city_df = london_df[london_df["town"] == "LONDON"]

city_df = city_df.drop(columns=["Dial\xa0code", "OS grid ref"])

print(city_df.head())

print(city_df["location"].unique())

# rename neighborhoods with multiple names to a single name
city_df[city_df["location"] == "Bromley (also Bromley-by-Bow)"] = "Bromley"
city_df[city_df["location"] == "Marylebone (also St Marylebone)"] = "Marylebone"
city_df[
    city_df["location"] == "Sydenham (also Lower Sydenham, Upper Sydenham)"
] = "Sydenham"

# create London neighborhood list
def get_neighborhood_list():
    neighborhood_list = []
    for neighborhood in city_df["location"]:
        if neighborhood in neighborhood_list:
            continue
        else:
            neighborhood_list.append(neighborhood)
    return neighborhood_list


london_neighborhoods = get_neighborhood_list()

# get latitude and longitude for each listed neighborhood
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


coordinates = get_geocodes(london_neighborhoods)

# delete neighborhood without coordinates
del coordinates["Somerstown"]

# Collecting pubs data from Foursquare API

pubs_category = "13018"
police_metro_categories = "19046,12072"

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
df.to_csv("city_of_london_pubs.csv")

# Collecting Subway and Police Data from Foursquare API

# collecting Police and Metro data
police_metro_data = get_venues_data(police_metro_categories)
print(len(police_metro_data))

# transform flattened list of police and metro venues data into pandas dataframe
police_metro_json = parse_json_list(police_metro_data)
print(len(police_metro_json))
df2 = pd.DataFrame(police_metro_json)
print(df2.head())

# check for duplicated venues data
print(df2.fsq_id.duplicated().value_counts())

# save dataframe into csv file
df2.to_csv("city_of_london_metro_police.csv")

# Venues detailed data from Foursquare API

# create a list with all Foursquare Ids of the pubs collected
id_list = []
for id in df.fsq_id:
    id_list.append(id)

print(id_list)

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
df3.to_csv("pubs_rich_data.csv")
