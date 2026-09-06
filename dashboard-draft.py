import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Crime Analytics Dashboard", layout="wide")

MAX_ROWS = 100000
@st.cache_data
def load_data():
    master_incidents = pd.read_csv('master_incidents.csv', nrows=MAX_ROWS)
    dates = pd.read_csv('dates.csv', nrows=MAX_ROWS)
    crime_types = pd.read_csv('crime_types.csv', nrows=MAX_ROWS)
    locations = pd.read_csv('locations.csv', nrows=MAX_ROWS)
    
    return master_incidents, dates, crime_types, locations

master_incidents, dates, crime_types, locations = load_data()

df = master_incidents.merge(dates, on='DateID', how='left')
df = df.merge(crime_types, on='CrimeTypeID', how='left')
df = df.merge(locations, on='LocationID', how='left')

# Sidebar
st.sidebar.title("🔎 Explore DataFrames")
dataset = st.sidebar.selectbox("Choose a dataset", ["Merged Dataset", "Master Incidents", "Dates", "Crime Types", "Locations"])
if dataset == "Merged Dataset":
    st.sidebar.dataframe(df.head(50))
elif dataset == "Master Incidents":
    st.sidebar.dataframe(master_incidents.head(50))
elif dataset == "Dates":
    st.sidebar.dataframe(dates.head(50))
elif dataset == "Crime Types":
    st.sidebar.dataframe(crime_types.head(50))
elif dataset == "Locations":
    st.sidebar.dataframe(locations.head(50))

# Main App
st.title("🚔 Crime Analytics Dashboard")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Overview", "📈 Time Series", "🕵️ Crime Types", "📍 Locations", "📈 Advanced Trends", "Deep Dive Analytics"])

# ===  Overview Tab
with tab1:
    st.header("Overall Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", f"{df['IncidentID'].nunique():,}")
    with col2:
        st.metric("Arrest Rate", f"{df['Arrest'].mean() * 100:.2f}%")
    with col3:
        st.metric("Domestic Rate", f"{df['Domestic'].mean() * 100:.2f}%")

    with col4:
        unique_beats = df['Beat'].nunique()
        st.metric("Beats Involved", f"{unique_beats:,}")
    


    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("📅 Incidents per Year")
        fig = px.histogram(df, x='Year', color_discrete_sequence=['#636EFA'])
        fig.update_traces(marker_line_color='black', marker_line_width=1)
        fig.update_layout(bargap=0.2)
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("🚔 Arrest Trend per Year")
        arrest_trend = df.groupby('Year')['Arrest'].mean().reset_index()
        arrest_trend['Arrest Rate (%)'] = arrest_trend['Arrest'] * 100
        
        fig_arrest = px.line(
            arrest_trend, 
            x='Year', 
            y='Arrest Rate (%)', 
            markers=True, 
            line_shape='spline',
            color_discrete_sequence=['#EF553B']
        )
        fig_arrest.update_traces(marker=dict(size=8))
        fig_arrest.update_layout(yaxis_title="Arrest Rate (%)", xaxis_title="Year")
        st.plotly_chart(fig_arrest, use_container_width=True)

    st.divider()

    deep3, deep4 = st.columns(2)

    with deep3:
        st.subheader("📍 Top 10 Locations for Crimes")
        loc_desc = df['Location Description'].value_counts().head(10).reset_index()
        loc_desc.columns = ['Location', 'Count']
        fig_loc_desc = px.bar(loc_desc, x='Count', y='Location', orientation='h',
                              color='Count', color_continuous_scale='magma')
        fig_loc_desc.update_layout(yaxis_title="", xaxis_title="Incidents", bargap=0.3)
        st.plotly_chart(fig_loc_desc, use_container_width=True)

    with deep4:
        st.subheader("🧩 Crimes by FBI Code")
        fbi_code = df['FBI Code'].value_counts().head(10).reset_index()
        fbi_code.columns = ['FBI Code', 'Count']
        fig_fbi = px.bar(fbi_code, x='Count', y='FBI Code', orientation='h',
                         color='Count', color_continuous_scale='viridis')
        fig_fbi.update_layout(yaxis_title="", xaxis_title="Incidents", bargap=0.3)
        st.plotly_chart(fig_fbi, use_container_width=True)

    st.divider()

# === Time Series Tab
with tab2:
    st.header("Crime Over Time")
    time_tab1, time_tab2 = st.columns(2)
    with time_tab1:
        st.subheader("Monthly Trend")
        monthly = df.groupby(['Year', 'Month Name']).size().reset_index(name='Incidents')
        monthly['Month'] = pd.to_datetime(monthly['Month Name'], format='%B').dt.month
        monthly = monthly.sort_values(['Year', 'Month'])
        fig_month = px.line(monthly, x='Month Name', y='Incidents', color='Year', markers=True)
        st.plotly_chart(fig_month, use_container_width=True)
    with time_tab2:
        st.subheader("Hourly Trend")
        hourly = df.groupby('Hour').size().reset_index(name='Incidents')
        fig_hour = px.bar(hourly, x='Hour', y='Incidents', color='Incidents', color_continuous_scale='viridis')
        fig_hour.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_hour, use_container_width=True)

# === Crime Type Tab
with tab3:
    st.header("Crime Types Analysis")
    type_tab1, type_tab2 = st.columns(2)
    with type_tab1:
        st.subheader("Top Crime Categories")
        crime_counts = df['Primary Type'].value_counts().reset_index()
        crime_counts.columns = ['Crime Type', 'Count']
        fig_crime = px.bar(crime_counts.head(10), x='Count', y='Crime Type', orientation='h', color='Count', color_continuous_scale='plasma')
        fig_crime.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_crime, use_container_width=True)
    with type_tab2:
        st.subheader("Crime Descriptions")
        selected_crime = st.selectbox("Select Crime Type", df['Primary Type'].unique())
        desc_counts = df[df['Primary Type'] == selected_crime]['Description'].value_counts().reset_index()
        desc_counts.columns = ['Description', 'Count']
        fig_desc = px.bar(desc_counts.head(10), x='Count', y='Description', orientation='h', color='Count', color_continuous_scale='cividis')
        fig_desc.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_desc, use_container_width=True)

# === Location Tab
with tab4:
    st.header("Location Insights")
    loc_tab1, loc_tab2 = st.columns(2)
    with loc_tab1:
        st.subheader("Incidents by District")
        district_counts = df['District'].value_counts().reset_index()
        district_counts.columns = ['District', 'Count']
        fig_district = px.bar(district_counts, x='District', y='Count', color='Count', color_continuous_scale='blues')
        fig_district.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_district, use_container_width=True)
    with loc_tab2:
        st.subheader("Top Dangerous Locations")
        location_counts = df['Location Description'].value_counts().reset_index()
        location_counts.columns = ['Location Description', 'Count']
        fig_location = px.bar(location_counts.head(10), x='Count', y='Location Description', orientation='h', color='Count', color_continuous_scale='oranges')
        fig_location.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_location, use_container_width=True)
    
    st.subheader("Crime Heatmap")
    fig_map = px.density_mapbox(
        df.dropna(subset=['Latitude', 'Longitude']),
        lat='Latitude', lon='Longitude',
        radius=10,
        center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
        zoom=10,
        mapbox_style="open-street-map"
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("📍 Crime Scatter Plot by Location")

    # Drop rows where latitude/longitude is missing
    scatter_data = df.dropna(subset=['Latitude', 'Longitude'])

    fig_scatter = px.scatter(
        scatter_data,
        x='Longitude',
        y='Latitude',
        color='Primary Type',
        hover_data=['Description', 'Location Description', 'Arrest', 'Domestic'],
        opacity=0.5,
        title="Crime Locations Colored by Primary Type",
        width=1000,
        height=600
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# === Advanced Insights Tab
with tab5:
    st.header("🚀 Advanced Insights")

    adv1, adv2 = st.columns(2)

    with adv1:
        st.subheader("Top 5 Crime Types by Arrest Rate")
        arrest_rates = df.groupby('Primary Type')['Arrest'].mean().reset_index()
        arrest_rates = arrest_rates.sort_values('Arrest', ascending=False).head(5)
        fig_arrest = px.bar(arrest_rates, x='Primary Type', y='Arrest', color='Arrest', color_continuous_scale='greens')
        fig_arrest.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_arrest, use_container_width=True)

    with adv2:
        st.subheader("Top 5 Hours for Crimes")
        top_hours = df['Hour'].value_counts().reset_index()
        top_hours.columns = ['Hour', 'Incidents']

        fig_hours = px.bar(top_hours.sort_values('Incidents', ascending=False).head(5),
                        x='Hour', y='Incidents',
                        color='Incidents', color_continuous_scale='reds')
        fig_hours.update_traces(marker_line_color='black', marker_line_width=1)
        st.plotly_chart(fig_hours, use_container_width=True)

        # st.plotly_chart(fig_hours, use_container_width=True)

    st.subheader("Domestic vs Non-Domestic")
    dom_counts = df['Domestic'].value_counts().reset_index()
    dom_counts.columns = ['Domestic', 'Count']
    fig_domestic = px.pie(dom_counts, values='Count', names='Domestic', color_discrete_sequence=['#FF6347', '#00BFFF'])
    st.plotly_chart(fig_domestic, use_container_width=True)



with tab6:
    st.header("🔬 Deep Dive Analytics")

    deep1, deep2 = st.columns(2)

    with deep1:
        st.subheader("🔎 Arrest vs Non-Arrested Incidents")
        arrest_counts = df['Arrest'].value_counts().reset_index()
        arrest_counts.columns = ['Arrested', 'Count']
        fig_arrest = px.pie(arrest_counts, names='Arrested', values='Count', 
                            color_discrete_sequence=px.colors.sequential.RdBu, hole=0.4)
        st.plotly_chart(fig_arrest, use_container_width=True)

    with deep2:
        st.subheader("🏠 Domestic vs Non-Domestic Crimes")
        domestic_counts = df['Domestic'].value_counts().reset_index()
        domestic_counts.columns = ['Domestic', 'Count']
        fig_domestic = px.pie(domestic_counts, names='Domestic', values='Count', 
                              color_discrete_sequence=px.colors.sequential.PuBuGn, hole=0.4)
        st.plotly_chart(fig_domestic, use_container_width=True)

    st.divider()

    deep3, deep4 = st.columns(2)

    with deep3:
        st.subheader("📍 Top 10 Locations for Crimes")
        loc_desc = df['Location Description'].value_counts().head(10).reset_index()
        loc_desc.columns = ['Location', 'Count']
        fig_loc_desc = px.bar(loc_desc, x='Count', y='Location', orientation='h',
                              color='Count', color_continuous_scale='magma')
        fig_loc_desc.update_layout(yaxis_title="", xaxis_title="Incidents", bargap=0.3)
        st.plotly_chart(fig_loc_desc, use_container_width=True)

    with deep4:
        st.subheader("🧩 Crimes by FBI Code")
        fbi_code = df['FBI Code'].value_counts().head(10).reset_index()
        fbi_code.columns = ['FBI Code', 'Count']
        fig_fbi = px.bar(fbi_code, x='Count', y='FBI Code', orientation='h',
                         color='Count', color_continuous_scale='viridis')
        fig_fbi.update_layout(yaxis_title="", xaxis_title="Incidents", bargap=0.3)
        st.plotly_chart(fig_fbi, use_container_width=True)

    st.divider()

    st.subheader("🗺️ Incidents Across Areas")

    # Grouping
    beat_counts = df['Beat'].value_counts().head(10).reset_index()
    beat_counts.columns = ['Beat', 'Count']

    district_counts = df['District'].value_counts().head(10).reset_index()
    district_counts.columns = ['District', 'Count']

    ward_counts = df['Ward'].value_counts().head(10).reset_index()
    ward_counts.columns = ['Ward', 'Count']

    community_counts = df['Community Area'].value_counts().head(10).reset_index()
    community_counts.columns = ['Community Area', 'Count']

    # Layout: Beats and Districts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚓 Top Beats")
        fig_beat = px.bar(beat_counts, x='Count', y='Beat', orientation='h', color='Count', color_continuous_scale='plasma')
        fig_beat.update_layout(yaxis_title="", xaxis_title="Incidents", bargap=0.3)
        st.plotly_chart(fig_beat, use_container_width=True)

    with col2:
        st.subheader("🏢 Top Districts")
        fig_districts = px.bar(district_counts, x='Count', y='District', orientation='h', color='Count', color_continuous_scale='cividis')
        fig_districts.update_layout(yaxis_title="", xaxis_title="Incidents", bargap=0.3)
        st.plotly_chart(fig_districts, use_container_width=True)

    # Layout: Wards and Communities
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🏛️ Top Wards")
        fig_ward = px.bar(ward_counts, x='Count', y='Ward', orientation='h', color='Count', color_continuous_scale='teal')
        fig_ward.update_layout(yaxis_title="", xaxis_title="Incidents", bargap=0.3)
        st.plotly_chart(fig_ward, use_container_width=True)

    with col4:
        st.subheader("🏘️ Top Community Areas")
        fig_community = px.bar(community_counts, x='Count', y='Community Area', orientation='h', color='Count', color_continuous_scale='pinkyl')
        fig_community.update_layout(yaxis_title="", xaxis_title="Incidents", bargap=0.3)
        st.plotly_chart(fig_community, use_container_width=True)
