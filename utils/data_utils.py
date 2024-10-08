import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import streamlit as st

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataframe by ensuring consistent column data types.
    """
    for column in df.columns:
        # Replace empty strings with NA
        if df[column].dtype == 'object':
            df[column] = df[column].replace('', pd.NA)
        
        # Attempt to convert numeric columns
        if is_numeric_dtype(df[column]):
            df[column] = pd.to_numeric(df[column], errors='coerce')
        
        # Convert datetime columns
        elif is_datetime64_any_dtype(df[column]):
            df[column] = pd.to_datetime(df[column], errors='coerce')
        
        # Convert all object columns to string
        if df[column].dtype == 'object':
            df[column] = df[column].astype(str)
    
    return df




def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    # Ensure column values are converted to strings and handle NaN values
                    df[column] = df[column].astype(str)  # Convert column to string
                    df = df[df[column].str.contains(user_text_input, na=False, case=False)]

    return df

# def extract_alphabetic_prefix(id_value):
#     """
#     Extracts the first two alphabetic characters from an ID.

#     Args:
#         id_value (str or int): The ID from which to extract the prefix.

#     Returns:
#         str: The first two alphabetic characters in uppercase.
#     """
#     import re
#     letters = re.findall(r'[A-Za-z]', str(id_value))
#     return ''.join(letters[:2]).upper()

def update_entries(old_df, latest_df, index_column, replace_with_empty=False):
    """
    Updates entries in old_df based on latest_df, with an option to replace with empty values.

    Args:
        old_df (pd.DataFrame): The old DataFrame to be updated.
        latest_df (pd.DataFrame): The latest DataFrame with updated values.
        index_column (str): The column name to be used as the index.
        replace_with_empty (bool): Whether to replace with empty values if latest_df has None.

    Returns:
        pd.DataFrame: The updated DataFrame.
    """
    if index_column not in old_df.columns or index_column not in latest_df.columns:
        raise ValueError("The selected index column must be present in both DataFrames.")

    # Set index for both DataFrames
    old_df.set_index(index_column, inplace=True)
    latest_df.set_index(index_column, inplace=True)

    # Update old_df with latest_df where non-empty values are present
    for column in latest_df.columns:
        if replace_with_empty:
            # Directly replace values from latest_df
            old_df[column] = latest_df[column].reindex(old_df.index)
        else:
            # Only replace non-NA values from latest_df
            non_na_mask = latest_df[column].notna()
            old_df.loc[non_na_mask.index[non_na_mask], column] = latest_df.loc[non_na_mask.index[non_na_mask], column]

    # Combine the two DataFrames, filling old_df with the missing entries from latest_df
    updated_df = latest_df.combine_first(old_df)

    # Reset the index to preserve the original structure
    updated_df.reset_index(inplace=True)

    return updated_df

