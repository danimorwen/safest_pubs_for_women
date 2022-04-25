# Police and Subway Data

# import police and metro dataframe
pol_sub_data = pd.read_csv("/content/raw-london-police-station-data.csv", index_col=[0])

# copy the dataframe
police = pol_sub_data.copy()
print(police.info())

# check and drop duplicated rows
print(police.duplicated().value_counts())
police = police.drop_duplicates()
print(police.shape)

# extract selected data from column with values in dictionaries
def extract_value(df, column, regex):
    return df[column].str.extract(regex)


police["geocodes"] = extract_value(police, "geocodes", "{'main':.\{(.*?)\}")
police["address"] = extract_value(police, "location", "{'address':.'(.*?)',")
police["locality"] = extract_value(police, "location", "'locality':.'(.*?)',")
police["neighborhood"] = extract_value(police, "location", "'neighborhood':.\['(.*)'\]")
police["postcode"] = extract_value(police, "location", "'postcode':.'(.*?)'")
police["category"] = extract_value(police, "categories", "'name':.'(.*?)'")

print(police.head())

# check for missing data
police[police["geocodes"].isnull()]

# assign the geocedes data missing
location = geolocator.geocode("E1 7JP")
police.loc[
    50, "geocodes"
] = f"'latitude': {location.latitude}, 'longitude': {location.longitude}"
print(police_metro.loc[50, "geocodes"])

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


get_lat_long(police)
print(police.head())

# drop columns that will not be use in this project
police = police.drop(columns=["categories", "geocodes", "location"], axis=1)

# save dataframe into csv
police.to_csv("data-wrangling-police_clean.csv")
