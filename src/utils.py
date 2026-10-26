"""Shared helpers used across pipeline stages."""

import pandas as pd

DATE_COLUMNS = ("period_start", "period_end")


def parse_date_columns(df: pd.DataFrame, errors: str = "coerce") -> dict:
    """Parse period_start / period_end into datetime.

    Args:
        df: Input DataFrame containing the date columns.
        errors: pandas to_datetime error handling ('coerce' or 'raise').

    Returns:
        Dict mapping column name -> parsed Series.
    """
    parsed = {}
    for column in DATE_COLUMNS:
        parsed[column] = pd.to_datetime(
            df[column],
            errors=errors,
            format="mixed",
        )
    return parsed