import streamlit as st
import pandas as pd
import plotly.express as px
# from sqlalchemy import create_engine
# from sqlalchemy.exc import SQLAlchemyError

st.set_page_config(page_title="Crime Analytics Dashboard", layout="wide")

MAX_ROWS = 100000

# def read_tables_to_dataframes(db_url="sqlite:////content/chicago_crime.db"):
#     """Read tables from SQLite database into pandas DataFrames."""
#     try:
#         # Create database engine
#         engine = create_engine(db_url)

#         # Test database connection
#         with engine.connect() as connection:
#             print("Database connection established successfully.")

#         # Read each table into a DataFrame
#         master_incidents_df = pd.read_sql("SELECT * FROM MasterIncidents", con=engine)
#         print("MasterIncidents table loaded into DataFrame.")

#         crime_types_df = pd.read_sql("SELECT * FROM Crime_Types", con=engine)
#         print("Crime_Types table loaded into DataFrame.")

#         locations_df = pd.read_sql("SELECT * FROM Locations", con=engine)
#         print("Locations table loaded into DataFrame.")

#         dates_df = pd.read_sql("SELECT * FROM Dates", con=engine)
#         print("Dates table loaded into DataFrame.")

#         return master_incidents_df, crime_types_df, locations_df, dates_df

#     except SQLAlchemyError as e:
#         print(f"Database error: {str(e)}")
#         raise
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         raise
#     finally:
#         # Dispose of the engine to close connections
#         if 'engine' in locals():
#             engine.dispose()

# Load Data
@st.cache_data
def load_data():
    master_incidents = pd.read_csv('master_incidents.csv', nrows=MAX_ROWS)
    dates = pd.read_csv('dates.csv', nrows=MAX_ROWS)
    crime_types = pd.read_csv('crime_types.csv', nrows=MAX_ROWS)
    locations = pd.read_csv('locations.csv', nrows=MAX_ROWS)
    return master_incidents, dates, crime_types, locations

master_incidents, dates, crime_types, locations = load_data()

# Merge Data
df = master_incidents.merge(dates, on='DateID', how='left')
df = df.merge(crime_types, on='CrimeTypeID', how='left')
df = df.merge(locations, on='LocationID', how='left')


#sidebar
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

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Overview", "📈 Time Series", "🕵️ Crime Types", "📍 Locations", "📈 Comparative Analysis", "📈 Arrest Trend"])

# === Overview Tab
with tab1:
    st.header("Overall Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", f"{1421722:,}")
    with col2:
        st.metric("Arrest Rate", f"{df['Arrest'].mean() * 100:.2f}%")
    with col3:
        st.metric("Domestic Rate", f"{df['Domestic'].mean() * 100:.2f}%")
    with col4:
        st.metric("Beats Involved", f"{3020:,}")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🏙️ Top 10 Blocks")
        top_blocks = df['Block'].value_counts().head(10).reset_index()
        top_blocks.columns = ['Block', 'Count']
        fig_blocks = px.bar(top_blocks, x='Count', y='Block', orientation='h', color='Count', color_continuous_scale='blues')
        st.plotly_chart(fig_blocks, use_container_width=True)

    with col2:
        st.markdown("### 🚔 Top 10 Crime Types")
        top_types = df['Primary Type'].value_counts().head(10).reset_index()
        top_types.columns = ['Crime Type', 'Count']
        fig_types = px.bar(top_types, x='Count', y='Crime Type', orientation='h', color='Count', color_continuous_scale='blues')
        st.plotly_chart(fig_types, use_container_width=True)

    with col3:
        st.markdown("### 🛡️ Top Arrest Districts")
        top_districts = df[df['Arrest'] == True]['District'].value_counts().head(10).reset_index()
        top_districts.columns = ['District', 'Arrests']
        fig_districts = px.bar(top_districts, x='Arrests', y='District', orientation='h', color='Arrests', color_continuous_scale='blues')
        st.plotly_chart(fig_districts, use_container_width=True)

    st.divider()

    deep3, deep4 = st.columns(2)
    with deep3:
        st.subheader("📍 Top 10 Locations for Crimes")
    
        # Calculate the top 10 locations for crimes
        loc_desc = df['Location Description'].value_counts().head(10).reset_index()
        loc_desc.columns = ['Location', 'Count']
        
        # Create a donut chart for the top 10 locations
        fig_loc = px.pie(
            loc_desc, 
            names='Location', 
            values='Count', 
            color='Count', 
            hole=0.4,
            title="Top 10 Crime Locations"
        )
        
        # Update chart layout for better styling
        fig_loc.update_layout(
            margin=dict(t=40, b=40, l=40, r=40),  # Add margins for better visualization
            title_x=0.5,  # Center title
            title_y=0.95,
            font=dict(size=14, family="Arial, sans-serif"),
            showlegend=True,  # Display legend for clarity
            uniformtext_minsize=12,  # Ensure text in the chart is clear and not too small
            uniformtext_mode='hide',  # Hide text outside the chart
        )
        
        st.plotly_chart(fig_loc, use_container_width=True)

    with deep4:
        st.subheader("🧩 Crime Frequency by FBI Code")

        # Get the top 10 most frequent FBI Codes
        fbi_code = df['FBI Code'].value_counts().reset_index()
        fbi_code.columns = ['FBI Code', 'Count']

        # Create a bar chart with FBI Code on the x-axis
        fig_fbi = px.bar(fbi_code, x='FBI Code', y='Count',
                        color='Count', color_continuous_scale='Blues')

        # Update layout for better appearance
        fig_fbi.update_layout(
            xaxis_title="FBI Code",
            yaxis_title="Incident Count",
            xaxis_tickangle=-45  # Tilt x-axis labels for better visibility
        )

        # Show the plot
        st.plotly_chart(fig_fbi, use_container_width=True)


    st.divider()

    
    

# === Time Series Tab
with tab2:
    st.header("📈 Crime Over Time")

    # --- Sidebar filter for Primary Type ---
    st.subheader("🔎 Filter Data")
    selected_types = st.multiselect(
        "Select Crime Types (Primary Type):",
        options=['All'] + sorted(df['Primary Type'].unique().tolist()),  # List of unique crime types with 'All' as the first option
        default=['All']  # Default to 'All' selected
    )

    # If 'All' is selected, show all data, otherwise filter based on selected types
    if 'All' in selected_types:
        filtered_df = df.copy()  # Show all data if 'All' is selected
    else:
        filtered_df = df[df['Primary Type'].isin(selected_types)]  # Filter the data based on selected types

    # If no crime types are selected and 'All' is not selected, show a message
    if not selected_types or (len(selected_types) == 1 and 'All' not in selected_types):
        st.warning("Please select at least one crime type to display the data.")
    else:
        left_col, right_col = st.columns(2)

        # -- Incidents per Year --
        with left_col:
            st.markdown("### 📅 Incidents per Year")
            fig_year = px.histogram(
                filtered_df, x='Year', color_discrete_sequence=['#006400']
            )
            fig_year.update_traces(marker_line_color='black', marker_line_width=1)
            fig_year.update_layout(height=400)
            st.plotly_chart(fig_year, use_container_width=True)

        # -- Arrest Rate per Year --
        with right_col:
            st.markdown("### 🚔 Arrest Rate per Year")
            arrest_trend = filtered_df.groupby('Year')['Arrest'].mean().reset_index()
            arrest_trend['Arrest Rate (%)'] = arrest_trend['Arrest'] * 100
            fig_arrest = px.line(
                arrest_trend,
                x='Year',
                y='Arrest Rate (%)',
                markers=True,
                line_shape='spline',
                color_discrete_sequence=['green']
            )
            fig_arrest.update_layout(height=400)
            st.plotly_chart(fig_arrest, use_container_width=True)

        st.divider()

        col1, col2 = st.columns(2)

        # -- Monthly Incident Trend --
        with col1:
            st.markdown("### 🗓️ Monthly Incident Trend")
            monthly = filtered_df.groupby(['Year', 'Month Name']).size().reset_index(name='Incidents')
            monthly['Month'] = pd.to_datetime(monthly['Month Name'], format='%B').dt.month
            monthly = monthly.sort_values(['Year', 'Month'])

            fig_month = px.line(
                monthly,
                x='Month Name',
                y='Incidents',
                color='Year',
                markers=True,
                line_shape='spline',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_month.update_layout(xaxis=dict(categoryorder='array', categoryarray=[
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]))
            st.plotly_chart(fig_month, use_container_width=True)

        # -- Hourly Trend --
        with col2:
            st.markdown("### 🕒 Hourly Incident Trend")
            hourly = filtered_df.groupby('Hour').size().reset_index(name='Incidents')
            fig_hour = px.bar(
                hourly,
                x='Hour',
                y='Incidents',
                color='Incidents',
                color_continuous_scale='viridis'
            )
            fig_hour.update_layout(height=400)
            st.plotly_chart(fig_hour, use_container_width=True)

        st.divider()

        st.markdown("## 📅 Daily and Weekly Incident Patterns")

        col3, col4 = st.columns(2)

        # -- Incidents per Day (Day Column) --
        with col3:
            st.markdown("### 📆 Incidents by Day of Month")
            daywise = filtered_df.groupby('Day').size().reset_index(name='Incidents')

            fig_day = px.bar(
                daywise,
                x='Day',
                y='Incidents',
                color='Incidents',
                color_continuous_scale='viridis',
            )
            fig_day.update_layout(height=400, xaxis_title="Day of the Month (1-31)")
            st.plotly_chart(fig_day, use_container_width=True)

        # -- Incidents per Weekday (mapped words) --
        with col4:
            st.markdown("### 📅 Incidents by Day of Week")

            # Map numeric weekday to names
            weekday_mapping = {
                0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                4: 'Friday', 5: 'Saturday', 6: 'Sunday'
            }
            filtered_df['Weekday Name'] = filtered_df['Weekday'].map(weekday_mapping)
            weekday = filtered_df.groupby('Weekday Name').size().reset_index(name='Incidents')

            fig_weekday = px.bar(
                weekday,
                x='Weekday Name',
                y='Incidents',
                color='Incidents',
                color_continuous_scale='viridis'
            )
            fig_weekday.update_layout(
                height=400,
                xaxis=dict(categoryorder='array', categoryarray=[
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
                ])
            )
            st.plotly_chart(fig_weekday, use_container_width=True)



# === Crime Types Tab
with tab3:
    st.header("Crime Types Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Crime Categories")
        crime_counts = df['Primary Type'].value_counts().head(10).reset_index()
        crime_counts.columns = ['Crime Type', 'Count']
        fig_crime = px.bar(crime_counts, x='Count', y='Crime Type', orientation='h', color='Count', color_continuous_scale='plasma')
        st.plotly_chart(fig_crime, use_container_width=True)

    with col2:
        st.subheader("Crime Descriptions")
        selected_crime = st.selectbox("Select Crime Type", df['Primary Type'].unique())
        desc_counts = df[df['Primary Type'] == selected_crime]['Description'].value_counts().head(10).reset_index()
        desc_counts.columns = ['Description', 'Count']
        fig_desc = px.bar(desc_counts, x='Count', y='Description', orientation='h', color='Count', color_continuous_scale='cividis')
        st.plotly_chart(fig_desc, use_container_width=True)

    district_counts = df.groupby('District').size().reset_index(name='Incident Count')

    
# Step 2: Get the latitude and longitude of each district (assuming you have these columns)
    district_coords = df.groupby('District').agg({'Latitude': 'mean', 'Longitude': 'mean'}).reset_index()

    # Merge the district counts with the district coordinates
    district_data = pd.merge(district_counts, district_coords, on='District')


    st.subheader("Crime Frequency By District")

    # Step 3: Create a Cartogram-style scatter map (size and color represent incident count)
    fig_cartogram = px.scatter_mapbox(
        district_data, 
        lat='Latitude', 
        lon='Longitude', 
        size='Incident Count',  
        color='Incident Count',  
        color_continuous_scale='YlOrRd',  
        hover_name='District',  
        hover_data=['Incident Count'],  
        size_max=30,  
        title="Crime Incidents by District",  
    )

    
    fig_cartogram.update_layout(
        mapbox_style="open-street-map",  
        margin={"r":0,"t":40,"l":0,"b":0},  
        height=600,
        title_font=dict(size=24, family="Arial, sans-serif", color="black"),  
        geo=dict(
            showland=True,
            landcolor='rgb(255, 255, 255)',
            subunitcolor='rgb(255, 255, 255)',
            countrycolor='rgb(255, 255, 255)'
        )
    )

    # Step 5: Add labels for districts on the map
    for i, row in district_data.iterrows():
        fig_cartogram.add_annotation(
            x=row['Longitude'],
            y=row['Latitude'],
            text=row['District'],  # Label the district name
            showarrow=False,
            font=dict(size=10, color='black'),  # Font style for labels
            align='center'
        )

    # Step 6: Display the cartogram on Streamlit
    st.plotly_chart(fig_cartogram, use_container_width=True)

# === Locations Tab
with tab4:
    st.header("Location Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Incidents by District")
        district_counts = df['District'].value_counts().reset_index()
        district_counts.columns = ['District', 'Count']
        fig_district = px.bar(district_counts, x='District', y='Count', color='Count', color_continuous_scale='purples')
        st.plotly_chart(fig_district, use_container_width=True)

    with col2:
        st.subheader("Top Dangerous Locations")
        location_counts = df['Location Description'].value_counts().head(10).reset_index()
        location_counts.columns = ['Location Description', 'Count']
        fig_location = px.bar(location_counts, x='Count', y='Location Description', orientation='h', color='Count', color_continuous_scale='purples')
        st.plotly_chart(fig_location, use_container_width=True)

    st.header("Crime Type Proportions and Crime Density by District")
    
    # Dropdown for district selection in the main area
    selected_district = st.selectbox(
        "Select District:",
        options=['All'] + sorted(df['District'].dropna().unique().tolist())  # Add 'All' for the entire city
    )

    # Filter data based on selected district
    if selected_district != 'All':
        filtered_df = df[df['District'] == selected_district]
    else:
        filtered_df = df.copy()

    # Get the top 10 crime types based on the selected district
    top10_crime_types = filtered_df['Primary Type'].value_counts().head(10).index.tolist()
    filtered_df_top10 = filtered_df[filtered_df['Primary Type'].isin(top10_crime_types)]

    # Group by crime type and get the count of each type (for top 10 only)
    crime_type_counts = filtered_df_top10['Primary Type'].value_counts().reset_index()
    crime_type_counts.columns = ['Crime Type', 'Count']

    # st.divider()
    # Create a pie chart showing crime type proportions (only top 10)
    fig_pie = px.pie(
        crime_type_counts, 
        names='Crime Type', 
        values='Count',
        title=f"Top 10 Crime Type Proportions in District: {selected_district}" if selected_district != 'All' else "Top 10 Crime Type Proportions (All Districts)",
        color='Crime Type',  # This will color the pie chart segments by crime type
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Create the map showing crime density (heatmap by district)
    district_counts = df.groupby(['District', 'Latitude', 'Longitude']).size().reset_index(name='Crime Count')
    
    fig_map = px.density_mapbox(
        district_counts,
        lat='Latitude',
        lon='Longitude',
        z='Crime Count',
        radius=10,
        color_continuous_scale='Viridis',
        title=f"Crime Density Map for {selected_district}" if selected_district != 'All' else "Crime Density Map (All Districts)",
        mapbox_style="carto-positron",
    )

    # Set map size
    fig_map.update_layout(
        mapbox=dict(
            center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
            zoom=10,  # Adjust zoom level based on the region's density
        ),
        height=500
    )

    # Display the charts side by side in columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌍 Crime Density Heatmap")
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.subheader("Top 10 Crime Type Proportions")
        st.plotly_chart(fig_pie, use_container_width=True)

# === Advanced Trends Tab ===
with tab5:
    st.header("Comparative Analysis")

    time_unit = 'Year'  

    # Dropdown to select Crime Types for filtering
    crime_types = df['Primary Type'].unique().tolist()
    selected_crimes = st.multiselect("Select Crime Types", options=crime_types, default=crime_types)

    # Filtering the DataFrame based on selected crime types
    filtered_df = df[df['Primary Type'].isin(selected_crimes)]

    # Grouped data for Arrest over Time
    crime_time_arrest = filtered_df.groupby(['Year', 'Primary Type'])['Arrest'].mean().reset_index()

    # --- First Row of Charts ---
    col1, col2 = st.columns(2)

    with col1:
        fig_crime_arrest = px.line(
            crime_time_arrest, x=time_unit, y='Arrest', color='Primary Type',
            markers=True, title=f"Crime Type Arrest Rates Over Time (Aggregated by {time_unit})"
        )
        st.plotly_chart(fig_crime_arrest, use_container_width=True)

    with col2:
        crime_arrest_status = filtered_df.groupby(['Primary Type', 'Arrest']).size().reset_index(name='Count')
        crime_arrest_status['Arrest Status'] = crime_arrest_status['Arrest'].map({True: 'Arrest', False: 'Non-Arrest'})
        
        fig_bar = px.bar(
            crime_arrest_status, 
            x='Primary Type', 
            y='Count', 
            color='Arrest Status',
            barmode='group',
            title="Crime Types vs Arrest Status",
            labels={'Count': 'Number of Crimes', 'Primary Type': 'Crime Type'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- Second Row of Charts ---
    col3, col4 = st.columns(2)

    with col3:
        heatmap_data = crime_time_arrest.pivot(index='Primary Type', columns=time_unit, values='Arrest')
        fig_heatmap = px.imshow(
            heatmap_data,
            color_continuous_scale='Blues',
            labels={'x': time_unit, 'y': 'Crime Type', 'color': 'Arrest Rate'},
            title=f"Heatmap: Arrest Rate by Crime Type and {time_unit}"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with col4:
        fig_area = px.area(
            crime_time_arrest, x=time_unit, y='Arrest', color='Primary Type',
            title=f"Stacked Area Chart of Arrest Rates Over Time (by {time_unit})"
        )
        st.plotly_chart(fig_area, use_container_width=True)

    st.divider()

    # --- Third Row (full width for Bubble Chart) ---
    st.subheader("District-wise Crime and Arrest Analysis")

    crime_counts_district = df.groupby(['District', 'Primary Type']).size().reset_index(name='Crime Count')
    arrest_rates_district = df.groupby(['District', 'Primary Type'])['Arrest'].mean().reset_index(name='Arrest Rate')

    merged_data_district = pd.merge(crime_counts_district, arrest_rates_district, on=['District', 'Primary Type'])

    # Bubble chart: District vs Arrest Rate vs Number of Crimes
    crime_counts_district = df.groupby(['District', 'Primary Type']).size().reset_index(name='Crime Count')
    arrest_rates_district = df.groupby(['District', 'Primary Type'])['Arrest'].mean().reset_index(name='Arrest Rate')

    # Merge the crime counts and arrest rates data
    merged_data_district = pd.merge(crime_counts_district, arrest_rates_district, on=['District', 'Primary Type'])

    # Bubble chart: District vs Arrest Rate vs Number of Crimes
    fig_bubble = px.scatter(
        merged_data_district,
        x='District',  # District on the X-axis
        y='Arrest Rate',  # Arrest rate on the Y-axis
        size='Crime Count',  # Size of the bubble is based on number of crimes
        color='Primary Type',  # Different colors for different crime types
        hover_name='Primary Type',  # Hover text shows crime type
        title="Bubble Chart: District vs Arrest Rate vs Number of Crimes",
        labels={'Crime Count': 'Number of Crimes', 'Arrest Rate': 'Arrest Rate', 'District': 'District'},
        height=700,
    )

    st.plotly_chart(fig_bubble, use_container_width=True)




# === 🏆 Crime Frequency Leaderboard (Top 10)
with tab6:

    # Helper for Time of Day
    def time_of_day(hour):
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"

    df['Time of Day'] = df['Hour'].apply(time_of_day)

    st.subheader("Arrest Rate by Location and Time of Day")

    # Top 10 Locations based on number of incidents
    top10_locations = df['Location Description'].value_counts().head(10).index.tolist()

    heatmap_data = df[df['Location Description'].isin(top10_locations)]
    heatmap_grouped = heatmap_data.groupby(['Time of Day', 'Location Description'])['Arrest'].mean().reset_index()
    heatmap_pivot = heatmap_grouped.pivot(index='Time of Day', columns='Location Description', values='Arrest')

    fig_heatmap = px.imshow(
        heatmap_pivot,
        text_auto=True,
        color_continuous_scale='Viridis',
        labels=dict(x="Location", y="Time of Day", color="Arrest Rate"),
    )

    # Stretch the heatmap: wider and taller
    fig_heatmap.update_layout(
        height=600, 
        width=2000,
        margin=dict(l=40, r=40, t=80, b=40)
    )

    st.plotly_chart(fig_heatmap, use_container_width=False)