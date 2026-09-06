import pandas as pd
import os

def load_data(filename=None):

  if not filename:
    return

  if not filename.endswith(".csv"):
    raise ValueError("Invalid file type. Please provide a CSV file.")

  df = pd.read_csv(filename)
  return df




from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder

def process_data(df=None):

  if df is None or df.empty:
        return None

  df.drop_duplicates(inplace=True)
  df.dropna( inplace=True)

    # Convert date columns to datetime
  df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
  df['Updated On'] = pd.to_datetime(df['Updated On'], errors='coerce')

  # Convert float fields that are supposed to be integers
  df['District'] = df['District'].astype('Int16')
  df['Ward'] = df['Ward'].astype('Int16')
  df['Community Area'] = df['Community Area'].astype('Int16')


  df['Month Name'] = df['Date'].dt.month_name()
  df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p')

  df['timestamp'] = df['Date']
  df['Year'] = df['Date'].dt.year
  df['Month'] = df['Date'].dt.month
  df['Day'] = df['Date'].dt.day
  df['Hour'] = df['Date'].dt.hour
  df['Weekday'] = df['Date'].dt.weekday

  if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'], inplace=True)



  scaler = StandardScaler()
  le = LabelEncoder()


  cols = ['Primary Type', 'Description', 'Location Description', 'Arrest', 'Domestic']

  for col in cols:
      encoded_col = le.fit_transform(df[col])
      df[col+' Encoded'] = encoded_col

  return df


def create_normalized_tables(df):
    """Create normalized tables from the DataFrame."""

    # 1. Crime_Types table
    crime_types = df[['Primary Type', 'Description', 'FBI Code']].drop_duplicates().reset_index(drop=True)
    crime_types['CrimeTypeID'] = crime_types.index + 1

    # 2. Locations table
    locations = df[['Block', 'Location Description', 'Latitude', 'Longitude',
                    'X Coordinate', 'Y Coordinate', 'Community Area', 'Ward', 'District', 'Beat']].drop_duplicates().reset_index(drop=True)
    locations['LocationID'] = locations.index + 1

    # 3. Date table
    date_df = df[['Date', 'Updated On', 'Year', 'Month', 'Day', 'Hour', 'Weekday',  'Month Name']].drop_duplicates().reset_index(drop=True)
    date_df['DateID'] = date_df.index + 1

    # Merge df to get CrimeTypeID
    df = df.merge(crime_types, on=['Primary Type', 'Description', 'FBI Code'], how='left')

    # Merge df to get LocationID
    df = df.merge(locations, on=['Block', 'Location Description', 'Latitude', 'Longitude',
                                 'X Coordinate', 'Y Coordinate', 'Community Area', 'Ward', 'District', 'Beat'], how='left')

    # Merge df to get DateID
    df = df.merge(date_df, on=['Date', 'Updated On', 'Year', 'Month', 'Day', 'Hour', 'Weekday', 'Month Name'], how='left')

    # Now build the final MasterIncidents table
    master_incidents = df[['ID', 'Case Number', 'DateID', 'CrimeTypeID', 'LocationID', 'Arrest', 'Domestic', 'Location Description Encoded']]

    master_incidents = master_incidents.rename(columns={'ID': 'IncidentID'})

    return master_incidents, crime_types, locations, date_df


import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import argparse
import os
from sqlalchemy.exc import SQLAlchemyError

def load_to_database(master_incidents, crime_types, locations, date_df, db_url="sqlite:////content/chicago_crime.db"):

    try:
        # Create a database engine
        # engine = create_engine(db_url)
        # with engine.connect() as connection:
        #     print("Database connection established successfully.")

        # Save master_incidents to CSV and database
        master_incidents.to_csv('master_incidents.csv', index=False)
        print("MasterIncidents saved to CSV.")
        # master_incidents.to_sql('MasterIncidents', con=engine, if_exists='replace', index=False)
        # print("MasterIncidents table saved to database.")

        # Save crime_types to CSV and database
        crime_types.to_csv('crime_types.csv', index=False)
        print("Crime_Types saved to CSV.")
        # crime_types.to_sql('Crime_Types', con=engine, if_exists='replace', index=False)
        # print("Crime_Types table saved to database.")

        # Save locations to CSV and database
        locations.to_csv('locations.csv', index=False)
        print("Locations saved to CSV.")
        # locations.to_sql('Locations', con=engine, if_exists='replace', index=False)
        # print("Locations table saved to database.")

        # Save date_df to CSV and database
        date_df.to_csv('dates.csv', index=False)
        print("Dates saved to CSV.")
        # date_df.to_sql('Dates', con=engine, if_exists='replace', index=False)
        # print("Dates table saved to database.")

        print("All data loaded to database and saved to CSVs successfully.")

    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise
    # finally:
        # if 'engine' in locals():
        #     engine.dispose()

def main(input_file, db_url):
    # Load the raw data
    df = load_data(input_file)

    # Process and engineer new features
    df = process_data(df)

    # Create normalized tables
    master_incidents, crime_types, locations, date_df = create_normalized_tables(df)

    # Load the data into the database
    load_to_database(master_incidents, crime_types, locations, date_df, db_url)

    # Save the processed data to a CSV file
    # df.to_csv(output_file, index=False)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    # Directly provide the arguments
    input_file = './Chicago_Crimes_2012_to_2017.csv'
    db_url = "sqlite:////chicago_crime.db"

    main(input_file, db_url)