# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd

from datetime import date, timedelta

from utils.stations import (
    read_agrimet_stations,
    filter_stations_by_state,
)

from utils.agrimet import (
    get_agrimet_daily,
)

from utils.transform import (
    create_qaqc_dataset,
)



from utils.config import (
    PCODES,
    OUTPUT_UNITS,
)



# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PNW AgriMet Data Downloader",
    page_icon="🌦️",
    layout="wide",
)


# ============================================================
# TITLE
# ============================================================

st.title(
    "🌦️ Pacific Northwest AgriMet Daily Data Downloader"
)

st.write(
    """
Download daily AgriMet weather data and create
an AgWeather-QAQC compatible dataset.
"""
)


# ============================================================
# LOAD STATIONS
# ============================================================

try:

    stations = read_agrimet_stations()

except Exception as exc:

    st.error(
        "Unable to load the AgriMet station file."
    )

    st.exception(exc)

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Station Selection"
)


# ============================================================
# STATE
# ============================================================

states = sorted(
    stations["state"]
    .dropna()
    .unique()
)


selected_state = st.sidebar.selectbox(
    "State",
    states,
)


# ============================================================
# FILTER STATIONS
# ============================================================

filtered_stations = (
    filter_stations_by_state(
        stations,
        selected_state,
    )
)


# ============================================================
# STATION
# ============================================================

station_options = (
    filtered_stations[
        "station_id"
    ]
    .tolist()
)


selected_station_id = (
    st.sidebar.selectbox(
        "Station",
        station_options,
    )
)


selected_station = (
    filtered_stations[
        filtered_stations["station_id"]
        == selected_station_id
    ]
    .iloc[0]
)

## --------------------
# Get station elevation
# ------------------------
elevation = selected_station["elevation"]

# ============================================================
# PARAMETER INFORMATION
# ============================================================

st.sidebar.divider()

st.sidebar.subheader(
    "Weather Parameters"
)

st.sidebar.write(
    """
The application downloads the following
AgriMet parameters:
"""
)

parameter_info = {

    "ETOS": (
        "eto",
        "Reference ET",
        "in/day",
    ),

    "PP": (
        "precip",
        "Precipitation",
        "inches",
    ),

    "SR": (
        "rs",
        "Solar radiation",
        "Langleys",
    ),

    "MX": (
        "tmax",
        "Maximum temperature",
        "°F",
    ),

    "MN": (
        "tmin",
        "Minimum temperature",
        "°F",
    ),

    "MM": (
        "tavg",
        "Mean temperature",
        "°F",
    ),

    "RHN": (
        "rhmin",
        "Minimum relative humidity",
        "%",
    ),

    "TA": (
        "rhavg",
        "Mean relative humidity",
        "%",
    ),

    "YM": (
        "tdew",
        "Mean dew point",
        "°F",
    ),

    "UA": (
        "uz",
        "Average wind speed",
        "mph",
    ),

    "WR": (
        "wind_run",
        "Wind run",
        "miles/day",
    ),

    "YW": (
        "avg_temp_soil",
        "Mean 4-inch soil temperature",
        "°F",
    ),
}


for pcode in PCODES:

    output_name, description, unit = (
        parameter_info[pcode]
    )

    st.sidebar.markdown(
        f"**{pcode}** → `{output_name}`  \n"
        f"{description} ({unit})"
    )


st.sidebar.markdown(
    """
**Calculated variables**

**ea** → Actual vapor pressure (kPa)

**rhmax** → `2 × rhavg − rhmin` (%)

**jul_date** → Day of year
"""
)


# ============================================================
# STATION INFORMATION
# ============================================================

st.subheader(
    f"{selected_station['station_id']} — "
    f"{selected_station['station_name']}"
)


col1, col2, col3, col4, col5 = (
    st.columns(5)
)


col1.metric(
    "Station ID",
    selected_station["station_id"],
)


col2.metric(
    "State",
    selected_station["state"],
)


if pd.notna(
    selected_station["latitude"]
):

    latitude = (
        f"{selected_station['latitude']:.5f}"
    )

else:

    latitude = "Unknown"


col3.metric(
    "Latitude",
    latitude,
)


if pd.notna(
    selected_station["longitude"]
):

    longitude = (
        f"{selected_station['longitude']:.5f}"
    )

else:

    longitude = "Unknown"


col4.metric(
    "Longitude",
    longitude,
)

#-----------
# Elevation
#-----------
if pd.notna(elevation):
    elevation_text = (
        f"{float(elevation):.1f} m"
    )
    
else:
    elevation_text = "Unknown"
    
col5.metric(
    "Elevation",
    elevation_text,
)


# ============================================================
# INSTALLATION DATE
# ============================================================

installation_date = (
    selected_station[
        "installed_date"
    ]
)


if pd.notna(
    installation_date
):

    installation_date = (
        installation_date.date()
    )

else:

    st.error(
        "Installation date is missing "
        "for this station."
    )

    st.stop()




# ============================================================
# AVAILABLE DATE RANGE
# ============================================================

today = date.today()

yesterday = (
    today
    - timedelta(days=1)
)


st.info(
    f"""
**Station installation date:** `{installation_date}`

**Latest allowed date:** `{yesterday}`

The application will not request data before
the station installation date or after yesterday.
"""
)


# ============================================================
# DATE SELECTORS
# ============================================================

date_col1, date_col2 = (
    st.columns(2)
)


with date_col1:

    start_date = st.date_input(
        "Start date",
        value=installation_date,
        min_value=installation_date,
        max_value=yesterday,
    )


with date_col2:

    end_date = st.date_input(
        "End date",
        value=yesterday,
        min_value=installation_date,
        max_value=yesterday,
    )


# ============================================================
# DATE VALIDATION
# ============================================================

if start_date > end_date:

    st.error(
        "Start date must be on or before "
        "the end date."
    )

    st.stop()


number_of_days = (
    end_date - start_date
).days + 1


st.success(
    f"""
Selected period: **{start_date} → {end_date}**

Total days requested: **{number_of_days:,}**
"""
)


# ============================================================
# DOWNLOAD
# ============================================================

st.divider()

download_clicked = st.button(
    "⬇️ Download AgriMet Data",
    type="primary",
    use_container_width=True,
)


if download_clicked:

    with st.spinner(
        "Downloading data from USBR AgriMet..."
    ):

        raw_df = get_agrimet_daily(
            station=selected_station_id,
            start_date=start_date,
            end_date=end_date,
            pcodes=PCODES,
        )


    # ========================================================
    # CHECK RAW DATA
    # ========================================================

    if raw_df.empty:

        st.error(
            f"No AgriMet data was returned for "
            f"station {selected_station_id}."
        )

        st.stop()


    # ========================================================
    # RAW DATA PREVIEW
    # ========================================================

    st.success(
        f"Downloaded {len(raw_df):,} raw AgriMet records."
    )

    st.subheader(
        "Raw AgriMet Data"
    )

    st.dataframe(
        raw_df,
        use_container_width=True,
        height=500,
    )


    # ========================================================
    # RAW CSV
    # ========================================================

    raw_csv = (
        raw_df
        .to_csv(
            index=False
        )
        .encode("utf-8")
    )


    raw_filename = (
        f"{selected_station_id}"
        f"_agrimet_raw_"
        f"{start_date.strftime('%Y%m%d')}"
        f"_"
        f"{end_date.strftime('%Y%m%d')}"
        f".csv"
    )


    st.download_button(

        label=(
            "💾 Download Option 1 — "
            "Original AgriMet Data"
        ),

        data=raw_csv,

        file_name=raw_filename,

        mime="text/csv",

        use_container_width=True,
    )


    # ========================================================
    # CREATE DATA for QAQC: it will have new column name
    # ========================================================

    qaqc_df = create_qaqc_dataset(
        raw_df=raw_df,
        station=selected_station_id,
    )


    # ========================================================
    # DATA PREVIEW
    # ========================================================

    st.divider()

    st.subheader(
        "Generating Data for AgWeather-QAQC"
    )

    st.dataframe(
        qaqc_df,
        use_container_width=True,
        height=500,
    )


    # ========================================================
    # Data CSV
    # ========================================================

    qaqc_export = qaqc_df.copy()


    # Format date as m/d/yyyy

    qaqc_export["date"] = (
        pd.to_datetime(
            qaqc_export["date"]
        )
        .apply(
            lambda x:
            f"{x.month}/"
            f"{x.day}/"
            f"{x.year}"
        )
    )


    qaqc_csv = (
        qaqc_export
        .to_csv(
            index=False
        )
        .encode("utf-8")
    )


    # ============================================================
    # CREATE QAQC FILENAME
    # ============================================================

    station_name = str(selected_station["station_name"]).strip()
    station_state = str(selected_station["state"]).strip()

    #Take text before the first comma

    station_name_short = station_name.split(",", 1)[0].strip()
    # Remove spaces from location name
    station_name_short = station_name_short.replace(" ", "")

    # Final filename
    qaqc_filename = (
        f"{station_name_short}"
        f"{station_state}"
        f"_Daily"
        f".csv"
    )


    st.download_button(

        label=(
            "💾 Download Option 2 — "
            "Get Data for AgWeather-QAQC Workflow"
        ),

        data=qaqc_csv,

        file_name=qaqc_filename,

        mime="text/csv",

        use_container_width=True,
    )


    # ========================================================
    # QAQC INFORMATION
    # ========================================================

    st.divider()

    st.subheader(
        "Final Data Column Information"
    )


    qaqc_info = pd.DataFrame({

        "column": qaqc_df.columns,

        "unit": [
            OUTPUT_UNITS.get(
                column,
                "",
            )
            for column in qaqc_df.columns
        ],

    })


    st.dataframe(
        qaqc_info,
        use_container_width=True,
        hide_index=True,
    )