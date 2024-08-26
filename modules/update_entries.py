import pandas as pd
import streamlit as st
from utils.file_utils import read_files, download_excel
from utils.data_utils import update_entries

def render_update_entries_page():
    st.sidebar.header("Update Entries")

    # Upload files for the old and latest data
    old_files = st.sidebar.file_uploader("Upload Old Files", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True, key='old_files')
    latest_files = st.sidebar.file_uploader("Upload Latest Files", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True, key='latest_files')

    if old_files and latest_files:
        old_df = read_files(old_files)
        latest_df = read_files(latest_files)

        if old_df.empty or latest_df.empty:
            st.error("One or both of the files could not be read.")
            return

        # Check for duplicate column names in both DataFrames
        if old_df.columns.duplicated().any() or latest_df.columns.duplicated().any():
            st.error("Duplicate column names detected. Please ensure each column has a unique name.")
            return

        # Allow the user to select the index column
        st.sidebar.subheader("Select Index Column")
        index_column = st.sidebar.selectbox(
            "Choose the index column for updating entries:",
            options=set(old_df.columns.tolist()) & set(latest_df.columns.tolist()),  # Only columns present in both DataFrames
            index=0
        )

        # Radio button for replace with empty values option
        replace_option = st.sidebar.radio(
            "Replace with empty values",
            ("Do not replace with empty values", "Replace with empty values"),
            index=0
        )
        replace_with_empty = replace_option == "Replace with empty values"

        # Perform the update
        try:
            updated_df = update_entries(old_df, latest_df, index_column, replace_with_empty=replace_with_empty)
            st.subheader("Updated Data")
            st.dataframe(updated_df, use_container_width=True)

            # Option to download the updated DataFrame as an Excel file
            download_excel(updated_df, "updated_data.xlsx")

        except ValueError as e:
            st.error(str(e))

    elif not old_files:
        st.info("Please upload the Old Files.")
    elif not latest_files:
        st.info("Please upload the Latest Files.")
