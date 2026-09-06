import pandas as pd
import os

# Reduce each CSV to 10% of its original rows
SAMPLE_FRACTION = 0.10

# CSV files to process
csv_files = [
    "Chicago_Crimes_2012_to_2017.csv",
    "crime_types.csv",
    "dates.csv",
    "locations.csv",
    "master_incidents.csv",
]

for file in csv_files:
    if not os.path.exists(file):
        print(f"SKIPPED: {file} - file not found")
        continue

    print(f"\nProcessing: {file}")

    # Read CSV
    df = pd.read_csv(file)

    original_rows = len(df)

    # Randomly select 10% of rows
    sampled_df = df.sample(
        frac=SAMPLE_FRACTION,
        random_state=42
    )

    # Shuffle again so the saved file isn't ordered by the original index
    sampled_df = sampled_df.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    # Overwrite the original file
    sampled_df.to_csv(
        file,
        index=False
    )

    # File size after compression/trimming
    size_mb = os.path.getsize(file) / (1024 * 1024)

    print(f"Original rows : {original_rows:,}")
    print(f"New rows      : {len(sampled_df):,}")
    print(f"Rows kept     : {len(sampled_df) / original_rows:.1%}")
    print(f"New file size : {size_mb:.2f} MB")

print("\nDone!")

