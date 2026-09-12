# Chicago Crimes Analytics Dashboard

A Streamlit dashboard for exploring Chicago crime incidents from 2012 to 2017. The project combines normalized crime, date, location, and incident tables to provide interactive summaries and visual analysis.

## Features

- Overview metrics for incidents, arrests, domestic incidents, and beats
- Crime frequency by year, month, day, weekday, and hour
- Arrest-rate trends over time
- Top crime types, descriptions, blocks, districts, and locations
- District-level maps and crime-density visualizations
- Comparative crime-type and arrest analysis
- Arrest rates by location and time of day
- Sidebar previews of each source table and the merged dataset

## Project Structure

| File                              | Purpose                                                  |
| --------------------------------- | -------------------------------------------------------- |
| `app.py`                          | Main Streamlit dashboard                                 |
| `dashboard-draft.py`              | Earlier dashboard implementation                         |
| `script.py`                       | Cleans the raw dataset and creates normalized CSV tables |
| `trim_dataset.py`                 | Destructively samples each CSV to 10% of its rows        |
| `Chicago_Crimes_2012_to_2017.csv` | Raw Chicago crime dataset used as the pipeline input     |
| `master_incidents.csv`            | Incident-level fact table                                |
| `crime_types.csv`                 | Crime type, description, and FBI code lookup table       |
| `locations.csv`                   | Location and geographic lookup table                     |
| `dates.csv`                       | Date and time lookup table                               |
| `requirements.txt`                | Core dashboard dependencies                              |
| `sol.ipynb`                       | Exploratory notebook                                     |
| `MA.pdf`                          | Project report or supporting material                    |

## Requirements

- Python 3.9 or newer
- The packages listed in `requirements.txt`
- A browser for viewing the Streamlit app

The preprocessing script also imports `scikit-learn` and `SQLAlchemy`. Install those packages if you plan to run the preprocessing pipeline:

```bash
python -m pip install -r requirements.txt
python -m pip install scikit-learn sqlalchemy
```

## Quick Start

The normalized CSV files are already included in the repository, so the dashboard can be started directly:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Rebuild the Data Tables

To regenerate the normalized tables from the raw Chicago crime dataset:

```bash
python -m pip install -r requirements.txt
python -m pip install scikit-learn sqlalchemy
python script.py
```

`script.py` reads `Chicago_Crimes_2012_to_2017.csv` and writes these files in the project directory:

- `master_incidents.csv`
- `crime_types.csv`
- `locations.csv`
- `dates.csv`

The pipeline removes duplicate and incomplete rows, derives date and time fields, encodes selected categorical fields, and creates lookup tables linked by `DateID`, `CrimeTypeID`, and `LocationID`.

## Data Model

The dashboard loads the four normalized CSV files and reconstructs a working dataset with these joins:

```text
master_incidents.DateID     -> dates.DateID
master_incidents.CrimeTypeID -> crime_types.CrimeTypeID
master_incidents.LocationID  -> locations.LocationID
```

The resulting merged dataset supplies incident measures, crime classifications, timestamps, and geographic fields for the charts and maps.

## Sampling the Dataset

`trim_dataset.py` keeps 10% of the rows in each listed CSV using a fixed random seed of `42`:

```bash
python trim_dataset.py
```

This script overwrites the existing CSV files. Make a backup first if the full datasets need to be preserved. Sampling the normalized tables independently can also break relationships between foreign keys and lookup rows, so use it only for local experimentation unless the tables are regenerated together.

## Notes

- `app.py` currently reads at most `100,000` rows from each normalized table through the `MAX_ROWS` constant.
- Run commands from the project root so the relative CSV paths resolve correctly.
- The dashboard expects the normalized CSV files to be present beside `app.py`.
- Plotly maps may require internet access when using an online map style or tile provider.

## Validation

To check the Python entry points without launching the dashboard:

```bash
python -m py_compile app.py script.py trim_dataset.py
```
