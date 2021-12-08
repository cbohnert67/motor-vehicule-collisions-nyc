import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
    "https://data.cityofnewyork.us/api/views/h9gi-nx95/rows.csv?accessType=DOWNLOAD"
)

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used \
to analyze motor vehicle collisions in NYC")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates=[["CRASH DATE", "CRASH TIME"]])
    data.dropna(subset=["LATITUDE", "LONGITUDE"], inplace = True)
    lowercase = lambda x: str(x).lower().replace(' ', '_')
    data.rename(lowercase, axis="columns", inplace=True)
    data.rename(columns = {'crash_date_crash_time':'date/time'}, inplace=True)
    return data


data = load_data(1847335)
original_data = data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicles collisions :", 1, 19)
#st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how="any"), zoom=10)

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": 40.680833,
        "longitude":  -73.97511,
        "zoom":10,
        "pitch": 50,
    },
    layers = [
        pdk.Layer(
            "HexagonLayer", 
            data=data.query("number_of_persons_injured >= @injured_people")[["date/time", "latitude", "longitude"]].dropna(how="any"),
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0,1000],
        ),
    ]

))




st.header("How many collisions occur during a given time of day ?")
hour = st.slider("Hour to look at :", 0, 23)
data = data[data["date/time"].dt.hour == hour]

st.markdown("Vehicle collisions between {}:00 and {}:00 :".format(hour, (hour+1)%24))


st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": 40.680833,
        "longitude":  -73.97511,
        "zoom":10,
        "pitch": 50,
    },
    layers = [
        pdk.Layer(
            "HexagonLayer", 
            data=data[["date/time", "latitude", "longitude"]],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0,1000],
        ),
    ]

))

st.subheader("Breakdown by minute between {}:00 and {}:00 :".format(hour, (hour+1)%24))
filtered = data[
    ((data["date/time"].dt.hour >= hour) & (data["date/time"].dt.hour<=(hour+1)))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x="minute", y = "crashes", hover_data = ["minute", "crashes"], height= 400)
st.write(fig)

st.header("What is the top 5 dangerous streets by affected people ")
select = st.selectbox("Affected type of people :", ["Pedestrians", "Cyclists", "Motorists"])

if select=="Pedestrians":
    st.write(original_data.query("number_of_pedestrians_injured>=1")[["on_street_name", "number_of_pedestrians_injured"]].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how="any")[:5])
elif select=="Cyclists":
    st.write(original_data.query("number_of_cyclist_injured >=1")[["on_street_name", "number_of_cyclist_injured"]].sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how="any")[:5])
else:
    st.write(original_data.query("number_of_motorist_injured>=1")[["on_street_name", 'number_of_motorist_injured']].sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how="any")[:5])





if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.write(data)



