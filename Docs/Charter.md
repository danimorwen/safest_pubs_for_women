# Project Charter

## Background

London is well-known for its pubs. With more than 3500 pubs in the city, it can be expected to be part of a Londoner life. It is not different for Londoner women, as they represent 48% of all pubs consumers. But women might be uncomfortable and feel unsafe to be out at night in pubs, since pubs can be male-dominant environments.

## Scope

* Clustering models to predict good and safe pubs for women in London

## Metrics

* To predict good and safer pubs for women in London.
* Distance between pubs and subway and police stations, number of crimes within a radius of 500m, user rating, popularity. 
* To find pubs that are at least 500m from a tube station and a police station, have an average or lower number of crimes in a radius of 500m, are popular, have a rating about the average or higher.

## Plan

* Data collection: Data about pubs, police stations, subway stations, crimes collected from Fousquare API, Web scrapping, csv files.
* Data Wrangling: cleaning data, removing unwanted data, dealing with missing values.
* Data Tidying: merging separated information into one dataframe, creating variables in the pubs dataframe about crimes, subway and police stations related to a pub.
* EDA: Analyzing pubs and their surroundings through graphs.
* Modelling: build and evaluate K-Means clustering models.

## Architecture

* Data
  * Raw: Foursquare API, CSV FIles
 
* Tools and libraries:
  * Python
  * Requests, Selenium, BeautifulSoup, Geopy
  * Pandas, Numpy, Harversine
  * Seaborn, Matplotlib, Folium
  * Scikit-learn, Yellowbrick
