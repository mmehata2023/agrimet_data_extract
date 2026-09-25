# ============================================================
# STATION FUNCTIONS
# ============================================================

import pandas as pd

from .config import STATION_FILE


# ============================================================
# READ AGRIMET STATIONS
# ============================================================

def read_agrimet_stations():

    stations = pd.read_csv(
        STATION_FILE,
        encoding="latin1"
    )

    stations.columns = (
        stations.columns
        .astype(str)
        .str.strip()
    )

    stations["station_id"] = (
        stations["station_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    stations["station_name"] = (
        stations["station_name"]
        .astype(str)
        .str.strip()
    )

    stations["state"] = (
        stations["state"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    stations["longitude"] = pd.to_numeric(
        stations["longitude"],
        errors="coerce",
    )

    stations["latitude"] = pd.to_numeric(
        stations["latitude"],
        errors="coerce",
    )

    stations["installed_date"] = pd.to_datetime(
        stations["installed_date"],
        errors="coerce",
    )

    stations = (
        stations
        .drop_duplicates(
            subset=["station_id"]
        )
        .reset_index(drop=True)
    )

    return stations


# ============================================================
# FILTER BY STATE
# ============================================================

def filter_stations_by_state(
    stations,
    state,
):

    return stations[
        stations["state"] == state
    ].copy()