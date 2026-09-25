# ============================================================
# DATA TRANSFORMATION FUNCTIONS
# ============================================================

import numpy as np
import pandas as pd

from .config import (
    OUTPUT_MAPPING,
    FINAL_COLUMNS,
)


# ============================================================
# NORMALIZE MISSING VALUES
# ============================================================

def normalize_missing_values(df):

    missing_values = [

        "998877",
        "998877.0",

        "NO RECORD",

        "m",
        "M",

        "",
        " ",

        "-",

        "NA",
        "N/A",
        "na",
        "n/a",
    ]

    return df.replace(
        missing_values,
        np.nan,
    )


# ============================================================
# FIND AGRIMET PARAMETER COLUMN
# ============================================================

def find_parameter_column(
    df,
    station,
    pcode,
):

    expected_name = (
        f"{station} {pcode}"
    )

    for column in df.columns:

        if (
            str(column)
            .strip()
            .upper()
            == expected_name.upper()
        ):

            return column

    return None


# ============================================================
# CREATE AGWEATHER-QAQC DATA
# ============================================================

def create_qaqc_dataset(
    raw_df,
    station,
):

    if raw_df.empty:

        return pd.DataFrame()

    df = normalize_missing_values(
        raw_df.copy()
    )

    result = pd.DataFrame()

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    result["date"] = pd.to_datetime(
        df["DATE"],
        errors="coerce",
    )

    result = result[
        result["date"].notna()
    ].copy()

    # --------------------------------------------------------
    # Station ID
    # --------------------------------------------------------

    result["id"] = station

    # --------------------------------------------------------
    # Parameters
    # --------------------------------------------------------

    for pcode, output_name in (
        OUTPUT_MAPPING.items()
    ):

        column = find_parameter_column(
            df,
            station,
            pcode,
        )

        if column is None:

            result[output_name] = np.nan

        else:

            result[output_name] = pd.to_numeric(
                df.loc[
                    result.index,
                    column
                ],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Julian date
    # --------------------------------------------------------

    result["jul_date"] = (
        result["date"]
        .dt.dayofyear
    )

    # --------------------------------------------------------
    # Actual vapor pressure
    #
    # From mean dew point
    #
    # °F → °C
    # --------------------------------------------------------

    tdew_c = (
        result["tdew"] - 32.0
    ) * 5.0 / 9.0

    result["ea"] = np.where(

        result["tdew"].notna(),

        0.6108
        * np.exp(
            (
                17.27
                * tdew_c
            )
            /
            (
                tdew_c
                + 237.3
            )
        ),

        np.nan,
    )

    # --------------------------------------------------------
    # RHmax
    #
    # RHmax = 2 × RHavg − RHmin
    #
    # If RHmin is missing, RHmax remains missing.
    # --------------------------------------------------------

    result["rhmax"] = (
        2.0
        * result["rhavg"]
        - result["rhmin"]
    )

    result.loc[
        result["rhavg"].isna()
        |
        result["rhmin"].isna(),
        "rhmax",
    ] = np.nan

    # --------------------------------------------------------
    # Physical RH limits
    # --------------------------------------------------------

    result["rhmax"] = (
        result["rhmax"]
        .clip(
            lower=0,
            upper=100,
        )
    )

    # --------------------------------------------------------
    # Final column order
    # --------------------------------------------------------

    result = result[
        FINAL_COLUMNS
    ]

    return result