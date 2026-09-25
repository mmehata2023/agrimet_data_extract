# ============================================================
# AGRIMET DOWNLOAD FUNCTIONS
# ============================================================

import requests
import pandas as pd

from io import StringIO

from .config import (
    AGRIMET_DAILY_URL,
    USER_AGENT,
)


# ============================================================
# PARSE AGRIMET RESPONSE
# ============================================================

def parse_agrimet_response(raw_text):

    if not raw_text:
        return pd.DataFrame()

    lines = raw_text.splitlines()

    # Remove HTML
    lines = [
        line
        for line in lines
        if "</" not in line
    ]

    # Remove comments
    lines = [
        line
        for line in lines
        if not line.strip().startswith("#")
    ]

    # Remove blank lines
    lines = [
        line
        for line in lines
        if line.strip()
    ]

    # Find header
    header_idx = None

    for i, line in enumerate(lines):

        if (
            "DATE" in line.upper()
            and "," in line
        ):
            header_idx = i
            break

    if header_idx is None:
        return pd.DataFrame()

    header = lines[header_idx]

    data_lines = lines[
        header_idx + 1:
    ]

    clean_rows = []

    for line in data_lines:

        if "END DATA" in line.upper():
            continue

        parts = [
            x.strip()
            for x in line.split(",")
        ]

        clean_rows.append(
            ",".join(parts)
        )

    if not clean_rows:
        return pd.DataFrame()

    header_clean = ",".join(
        x.strip()
        for x in header.split(",")
    )

    csv_text = (
        header_clean
        + "\n"
        + "\n".join(clean_rows)
    )

    try:

        df = pd.read_csv(
            StringIO(csv_text),
            dtype=str,
        )

    except Exception:

        return pd.DataFrame()

    return df


# ============================================================
# DOWNLOAD AGRIMET DATA
# ============================================================

def get_agrimet_daily(
    station,
    start_date,
    end_date,
    pcodes,
):

    all_data = []

    for year in range(
        start_date.year,
        end_date.year + 1,
    ):

        if year == start_date.year:
            m1 = start_date.month
        else:
            m1 = 1

        if year == end_date.year:
            m2 = end_date.month
        else:
            m2 = 12
            
        if year == start_date.year:
            day_start = start_date.day
        else:
            day_start = 1

        if year == end_date.year:
            day_end = end_date.day
        else:
            # Last day of the year
            day_end = 31

        url = (
            f"{AGRIMET_DAILY_URL}?"
            f"station={station}"
            f"&year={year}"
            f"&month={m1}"
            f"&day={day_start}"
            f"&year={year}"
            f"&month={m2}"
            f"&day={day_end}"
        )

        for pcode in pcodes:

            url += (
                f"&pcode={pcode}"
            )

        try:

            response = requests.get(
                url,
                headers={
                    "User-Agent": USER_AGENT
                },
                timeout=120,
            )

            response.raise_for_status()

        except Exception:

            continue

        df = parse_agrimet_response(
            response.text
        )

        if df.empty:
            continue

        all_data.append(df)

    if not all_data:

        return pd.DataFrame()

    result = pd.concat(
        all_data,
        ignore_index=True,
    )
    # ============================================================
    # FILTER TO EXACT USER-SELECTED DATES
    # ============================================================

    if "DATE" in result.columns:

        result["DATE"] = pd.to_datetime(
            result["DATE"],
            errors="coerce",
        )

        result = result[
            (result["DATE"] >= pd.Timestamp(start_date))
            & (result["DATE"] <= pd.Timestamp(end_date))
        ].reset_index(drop=True)

        
    return result

