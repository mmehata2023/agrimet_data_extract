# ============================================================
# CONFIGURATION
# ============================================================

AGRIMET_DAILY_URL = (
    "https://www.usbr.gov/pn-bin/daily.pl"
)

STATION_FILE = (
    "data/stations/agrimet_stations.csv"
)

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/140.0 Safari/537.36"
)


# ============================================================
# AGRIMET PARAMETERS
# ============================================================

PCODES = [
    "ETOS",
    "PP",
    "SR",
    "MX",
    "MN",
    "MM",
    "RHN",
    "TA",
    "YM",
    "UA",
    "WR",
    "YW",
]


# ============================================================
# OUTPUT COLUMN MAPPING
# ============================================================

OUTPUT_MAPPING = {

    "ETOS": "eto",

    "PP": "precip",

    "SR": "rs",

    "MX": "tmax",

    "MN": "tmin",

    "MM": "tavg",

    "RHN": "rhmin",

    "TA": "rhavg",

    "YM": "tdew",

    "UA": "uz",

    "WR": "wind_run",

    "YW": "avg_temp_soil",
}


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

FINAL_COLUMNS = [

    "date",
    "id",
    "jul_date",

    "eto",
    "precip",
    "rs",
    "ea",

    "tmax",
    "tmin",
    "tavg",

    "rhmax",
    "rhmin",
    "rhavg",

    "tdew",

    "uz",
    "wind_run",

    "avg_temp_soil",
]


# ============================================================
# UNITS
# ============================================================

OUTPUT_UNITS = {

    "date": "date",

    "id": "station ID",

    "jul_date": "day of year",

    "eto": "in/day",

    "precip": "inches",

    "rs": "Langleys",

    "ea": "kPa",

    "tmax": "°F",

    "tmin": "°F",

    "tavg": "°F",

    "rhmax": "%",

    "rhmin": "%",

    "rhavg": "%",

    "tdew": "°F",

    "uz": "mph",

    "wind_run": "miles/day",

    "avg_temp_soil": "°F",
}