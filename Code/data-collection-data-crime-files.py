import glob
import pandas as pd

# Through glob, transform all data crime csv files into a single pandas dataframe
files = glob.glob("/content/*.csv")
frames = [pd.read_csv(file) for file in files]
df = pd.concat(frames)

# Check if dataframe is correct
print(df.shape)
print(df.head())

# Filter dataframe for a specific type of crime and assign this to a new dataframe
crimes_df = df[df["Crime type"] == "Violence and sexual offences"]
print(crimes_df.shape)

# Drop rows without latitude and longitude data
crimes_df.dropna(subset=["Longitude", "Latitude"], inplace=True)

# Check the updated dataframe
print(crimes_df.info())
print(df.head())

# save dataframe into csv file
crimes_df.to_csv("london_crimes.csv")
