# Police and Subway Data

# import police and metro dataframe
pol_sub_data = pd.read_csv("/content/city_of_london_metro_police.csv", index_col=[0])

# copy the dataframe
police_metro = pol_sub_data.copy()
print(police_metro.info())

# check and drop duplicated rows
print(police_metro.duplicated().value_counts())
police_metro = police_metro.drop_duplicates()
print(police_metro.shape)

# extract selected data from column with values in dictionaries
def extract_value(df, column, regex):
    return df[column].str.extract(regex)


police_metro["geocodes"] = extract_value(police_metro, "geocodes", "{'main':.\{(.*?)\}")
police_metro["address"] = extract_value(
    police_metro, "location", "{'address':.'(.*?)',"
)
police_metro["locality"] = extract_value(
    police_metro, "location", "'locality':.'(.*?)',"
)
police_metro["neighborhood"] = extract_value(
    police_metro, "location", "'neighborhood':.\['(.*)'\]"
)
police_metro["postcode"] = extract_value(
    police_metro, "location", "'postcode':.'(.*?)'"
)
police_metro["category"] = extract_value(police_metro, "categories", "'name':.'(.*?)'")

print(police_metro.head())

# check for missing data
police_metro[police_metro["geocodes"].isnull()]

# assign the geocedes data missing
location = geolocator.geocode("SW9 9AE")
police_metro.loc[
    174, "geocodes"
] = f"'latitude': {location.latitude}, 'longitude': {location.longitude}"
print(police_metro.loc[174, "geocodes"])

##divide the geocode column into two new columns: latitude and longitude
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


get_lat_long(police_metro)
print(police_metro.head())

# drop columns that will not be use in this project
police_metro = police_metro.drop(columns=["categories", "geocodes", "location"], axis=1)

# save dataframe into csv
police_metro.to_csv("police_metro_clean.csv")
