import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import math
import base64
import numpy as np
import pydeck as pdk
import streamlit.components.v1 as components

# Haversine formula example in Python
# Author: Wayne Dyck
# https://en.wikipedia.org/wiki/Haversine_formula


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}">Download as CSV file</a>'
    return href


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d


def write():
    st.subheader("Data Cleaning")
    data_file = st.file_uploader("Upload CSV", type=['csv'])
    if data_file is not None:
        # Drop location duplicates
        st.success(
            'If multiple rows have the same GPS coordinates, only the last one is kept.')
        df = pd.read_csv(data_file)
        # Renaming id column
        df.columns = df.columns.str.lower()

        df = df.drop_duplicates(subset=['latitude', 'longitude'], keep='last')
        df = df.reset_index(drop=True)
        file_details = {"File size": data_file.size,
                        "Data rows": len(df)}
        # st.write(file_details)

        # Adding a distance
        df_d = df.assign(distance=0)
        for i in range(len(df_d)-1):
            j = i+1
            df_d.loc[j, 'distance'] = round(distance((df_d.latitude[i],
                                                      df_d.longitude[i]),
                                                     (df_d.latitude[j],
                                                      df_d.longitude[j]))*1000, 2)

        # Filtering for min. and max. distances
        st.subheader('Plausibility tests')
        data_points = len(df_d)
        slide_max = int(df_d['distance'].max())+10

        dist = st.slider('Select a range of plausible distances beween observations to be included: ', 0,
                         slide_max, (0, 200))
        df_d = df_d[(df_d['distance'] >= dist[0])
                    & (df_d['distance'] <= dist[1])]

        filtered_points = len(df_d)
        message = 'Minimum distance is ' + str(dist[0]) + ' meters and maximum distance is ' + str(dist[1]) + ' meters. Your data are reduced by: ' + \
            str(round(100 * (1 - filtered_points / data_points), 2)) + \
            ' %. Using the slider, you can change these values and see the effect in the table below. There are ' + \
            str(filtered_points) + ' data rows now.'
        st.success(message)

        # Display DataFrame
        df_d = df_d.reset_index(drop=True)
        st.dataframe(df_d[['time', 'latitude', 'longitude', 'distance', 'sats', 'precision', 'category']].style.background_gradient(
            subset=['distance', 'precision'], cmap='Blues'
        ))

        # Safe new data frame
        st.markdown(get_table_download_link(df_d), unsafe_allow_html=True)

        # Pairwise Viz
        st.subheader("Pairwise comparison of mapping data")
        fig2 = plt.subplots()
        fig2 = sns.pairplot(
            df_d[['latitude', 'longitude', 'rawtime',
                  'category', 'distance']],
            markers=["o", "s", "D", "*"])  # hue='Category'
        st.pyplot(fig2)

        # Use of categories
        col1, col2 = st.beta_columns(2)
        col1.info('This bar chart shows the usage frequency per category.')
        cat = df_d[['category']].groupby(['category']).size()

        catSeries = pd.Series([0, 0, 0, 0, 0, 0])
        catSeries = catSeries[1:6]
        for x in cat.index:
            catSeries[x] = cat[x]
        fig, ax = plt.subplots()
        ax = sns.barplot(x=catSeries.index, y=catSeries)
        col1.pyplot(fig)

        # GPS quality
        col2.info(
            'This bar chart indicates the quality of your GPS coordinates. 5+ is good.')
        satDistribution = df_d.groupby(
            df_d['sats']).size().sort_values(ascending=False)
        satNum = list(satDistribution.keys())
        satFreq = list(satDistribution)
        fig2, ax2 = plt.subplots()
        ax2 = sns.barplot(x=satNum, y=satFreq)
        col2.pyplot(fig2)

        # category coloring
        # tracks_d = categories.assign(Distance=0)
        df_d['color'] = ""
        df_d['color'] = df_d['color'].astype('object')

        cat_color = {
            1: [0, 0, 255, 250],  # Blue
            2: [255, 0, 0, 250],  # Red
            3: [0, 255, 0, 250],   # Green
            4: [255, 106, 0, 250],  # Orange
            5: [0, 88, 0, 250]        # Dark Green
        }
        for i in range(len(df_d)):
            df_d.at[i, 'color'] = cat_color[df_d.at[i, 'category']]

        st.subheader("Data Map")
        st.info(
            "... let's draw maps! You can choose the size of markers (4-12 is recommended) and the map's background.")
        marker = st.number_input('Marker Size: ', min_value=2, value=8)

        MapColor = {
            "Dark": 'mapbox://styles/innodesign/ckl128luk027z17mwftpdxyg1',
            "Light": 'mapbox://styles/mapbox/streets-v8',
        }
        map_col = st.radio("Map Background: ", list(MapColor.keys()))

        data = df_d[['latitude', 'longitude', 'color']]
        midpoint = (np.average(data['latitude']),
                    np.average(data['longitude']))
        st.info('Centre coordinates of the map: ' +
                str(round(midpoint[0], 4)) + ' and ' + str(round(midpoint[1], 4)))
        components.html(
            """
          <h4 style="font-family: Verdana, sans-serif">Color coding of categories:</h4>
    <ul style="font-family: Verdana, sans-serif; background-color: rgb(219, 213, 213)">
        <li style="color: rgb(0, 0, 255); list-style: none; background-color: rgb(219, 213, 213)"> Category 1: Blue</li>
        <li style="color: rgb(255, 0, 0); list-style: none; background-color: rgb(219, 213, 213)">Category 2: Red</li>
        <li style="color: rgb(0, 255, 0); list-style: none; background-color: rgb(219, 213, 213)">Category 3: Green</li>
        <li style="color: rgb(255, 106, 0); list-style: none; background-color: rgb(219, 213, 213)">Category 4: Orange</li>
        <li style="color: rgb(0, 88, 0); list-style: none; background-color: rgb(219, 213, 213)">Category 5: Dark Green</li>
        <li style="color: rgb(219, 213, 213); list-style: none; background-color: rgb(219, 213, 213)"..<li>
    </ul>
      """, height=180
        )

        st.pydeck_chart(pdk.Deck(
            # map_style='mapbox://styles/mapbox/dark-v9',
            # map_style='mapbox://styles/mapbox/streets-v8',
            map_style=MapColor[map_col],
            initial_view_state=pdk.ViewState(latitude=midpoint[0],
                                             longitude=midpoint[1],
                                             zoom=13,
                                             pitch=0,
                                             ),
            layers=pdk.Layer(
                "ScatterplotLayer",
                # type='HexagonLayer' / ScatterplotLayer / PointCloudLayer,
                data=data,
                get_position='[longitude, latitude]',
                elevation_scale=4,
                get_fill_color='color',
                get_radius=marker,
                opacity=0.5,
                filled=True
            )
        ))
        st.info('The heatmap below gives an impression of those areas, where most observations have been mapped. The more you zoom in, the more fine grained the aggregation becomes.')
        st.pydeck_chart(pdk.Deck(
            map_style=MapColor[map_col],
            initial_view_state=pdk.ViewState(latitude=midpoint[0],
                                             longitude=midpoint[1],
                                             zoom=13,
                                             pitch=0,
                                             ),
            layers=pdk.Layer(
                "HeatmapLayer",
                data=data,
                get_position='[longitude, latitude]',
                get_fill_color='color',
                opacity=0.9,
                aggregation='MEAN',
            )
        ))


if __name__ == "__main__":
    write()
