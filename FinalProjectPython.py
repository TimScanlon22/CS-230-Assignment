import pandas as pd
import geopy as geopy
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import shapely
import plotly_express as px
from geopy.geocoders import Nominatim
from shapely.geometry import Point
import scipy.spatial as spatial
import streamlit as st

def read_data(filename):
    columns = ['Resource Name', 'County', 'National Register Date', 'National Register Number', 'Longitude', 'Latitude', 'Georeference']
    data = pd.read_csv(filename, usecols=columns)
    data.dropna(axis = 1, inplace = True)
    return data

def county_freq(data):
    dataNew = dict(data.groupby(['County'])['Resource Name'].count())
    return dataNew

def close_by(data, pt, location, lst, otherLst):
    close_locations = []
    long = []
    lati = []
    nothalist = []
    for index, row in data.iterrows():
        long.append(float(row['Longitude']))
        lati.append(float(row['Latitude']))
    nothalist = zip(long, lati)
    close_locations = [shapely.geometry.Point(lat, lon) for lat, lon in zip(lati, long)]
    gdf = gpd.GeoDataFrame(data, geometry=close_locations, crs={"init":"EPSG:4326"})
    pts = gdf.geometry.unary_union
    ptsArray = np.array(pts)
    point_tree = spatial.KDTree(ptsArray)
    query = point_tree.query_ball_point((location.latitude, location.longitude), 0.35)
    st.write(query)
    for i in range(len(query)):
        value = query[i]
        lst.append(gdf.iloc[value])
        otherLst.append(gdf.iloc[value]['Resource Name'])
    st.write("List of Nearby National Parks")
    st.write(otherLst)

def bar_chart(x,y, column_width):
     plt.bar(x, y, width= column_width)
     plt.xticks(rotation = 90, fontsize = 6)
     plt.xlabel("County")
     plt.ylabel("Frequency")
     plt.ylim(0, 700)
     plt.title("Frequency of National Parks By County")
     return plt


def display_map(data, otherLst):
    local = []
    for index, row in data.iterrows():
        if row['Resource Name'] in otherLst:
            local.append([row['Resource Name'], row['Longitude'], row['Latitude']])
    df = pd.DataFrame(local, columns = ['Resource Name', 'Longitude', 'Latitude'])
    fig = px.scatter_mapbox(df, lat=df['Latitude'], lon=df['Longitude'], hover_name=df["Resource Name"], hover_data=[df["Longitude"], df["Latitude"]],
                        color_discrete_sequence=["fuchsia"], zoom=3, height=300)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def main():
    filename = 'National_Register_of_Historic_Places (3).csv'
    data = read_data(filename)
    st.title("Finding NY National Parks Near You")
    streetNum = st.text_input("Enter your number")
    streetName = st.text_input("Enter Your Street Name")
    city = st.text_input("Enter your city")
    lst =[]
    otherLst = []
    counties = []
    geolocator = Nominatim(user_agent="Final_Project_Python")
    location = geolocator.geocode(f"{streetNum} {streetName} {city} ")
    pt = Point(location.longitude, location.latitude)
    close_by(data, pt, location, lst, otherLst)
    st.write('Map of Nearby Locations')
    st.plotly_chart(display_map(data, otherLst))
    count_county = county_freq(data)
    counties = []
    for i in count_county:
        counties.append(i)
    counts = []
    for i in count_county:
        counts.append(count_county.get(i))
    column_width = st.slider('Width', 0.25, 0.50, 0.75)
    countiesList = data['County'].drop_duplicates()
    county = st.sidebar.selectbox("Select counties to filter by", countiesList)
    newCounts = []
    newCounts.append(count_county.get(county))
    st.pyplot(bar_chart(county, newCounts, column_width))




main()
