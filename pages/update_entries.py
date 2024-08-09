import pandas as pd
import streamlit as st
from utils.file_utils import read_excel_files, download_excel

def read_file(file, file_type):
    """
    Reads a file based on its type and returns a DataFrame.

    Args:
        file (UploadedFile): The uploaded file.
        file_type (str): The type of the file ('csv' or 'excel').

    Returns:
        pd.DataFrame: The DataFrame containing the file's data.
    """
    if file_type == 'csv':
        return pd.read_csv(file)
    elif file_type in ['xlsx', 'xls']:
        return pd.read_excel(file)
    else:
        st.error(f"Unsupported file type: {file_type}")
        return None

def render_update_entries_page():
    st.sidebar.header("Update Entries")

    # Upload files for the old and latest data
    old_file = st.sidebar.file_uploader("Upload Old File", type=['csv', 'xlsx', 'xls'], key='old_file')
    latest_file = st.sidebar.file_uploader("Upload Latest File", type=['csv', 'xlsx', 'xls'], key='latest_file')

    # Radio button for replace with empty values option
    replace_option = st.sidebar.radio(
        "Replace with empty values",
        ("Do not replace with empty values", "Replace with empty values"),
        index=0
    )

    # Determine if replacement should occur
    replace_with_empty = replace_option == "Replace with empty values"

    # Display information if both files are uploaded
    if old_file and latest_file:
        # Determine file types
        old_file_type = old_file.name.split('.')[-1]
        latest_file_type = latest_file.name.split('.')[-1]

        # Read the files into DataFrames
        old_df = read_file(old_file, old_file_type)
        latest_df = read_file(latest_file, latest_file_type)

        if old_df is not None and latest_df is not None:
            # Update entries in old_df based on latest_df
            updated_df = update_entries(old_df, latest_df, replace_with_empty=replace_with_empty)

            st.subheader("Updated Data")
            st.dataframe(updated_df, use_container_width=True)

            # Option to download the updated DataFrame as an Excel file
            download_excel(updated_df, "updated_data.xlsx")

    elif not old_file:
        st.info("Please upload the Old File.")
    elif not latest_file:
        st.info("Please upload the Latest File.")
