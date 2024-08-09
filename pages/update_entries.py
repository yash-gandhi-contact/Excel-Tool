import pandas as pd
import streamlit as st
from utils.file_utils import read_files, download_excel
from utils.data_utils import update_entries

def render_update_entries_page():
    st.sidebar.header("Update Entries")

    # Upload files for the old and latest data
    old_files = st.sidebar.file_uploader("Upload Old Files", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True, key='old_files')
    latest_files = st.sidebar.file_uploader("Upload Latest Files", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True, key='latest_files')

    # Radio button for replace with empty values option
    replace_option = st.sidebar.radio(
        "Replace with empty values",
        ("Do not replace with empty values", "Replace with empty values"),
        index=0
    )

    # Determine if replacement should occur
    replace_with_empty = replace_option == "Replace with empty values"

    # Display information if both sets of files are uploaded
    if old_files and latest_files:
        old_df = read_files(old_files)
        latest_df = read_files(latest_files)

        if old_df.empty or latest_df.empty:
            st.error("One or both of the files could not be read.")
        else:
            # Update entries in old_df based on latest_df
            updated_df = update_entries(old_df, latest_df, replace_with_empty=replace_with_empty)

            st.subheader("Updated Data")
            st.dataframe(updated_df, use_container_width=True)

            # Option to download the updated DataFrame as an Excel file
            download_excel(updated_df, "updated_data.xlsx")

    elif not old_files:
        st.info("Please upload the Old Files.")
    elif not latest_files:
        st.info("Please upload the Latest Files.")
