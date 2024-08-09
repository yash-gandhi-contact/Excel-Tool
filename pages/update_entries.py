import pandas as pd
import streamlit as st
from utils.file_utils import read_excel_files, download_excel
from utils.data_utils import update_entries

def render_update_entries_page():
    st.sidebar.header("Update Entries")

    # Upload files for the old and latest Excel
    old_excel = st.sidebar.file_uploader("Upload Old Excel", type=['xlsx', 'xls'], key='old_excel')
    latest_excel = st.sidebar.file_uploader("Upload Latest Excel", type=['xlsx', 'xls'], key='latest_excel')

    # Radio button for replace with empty values option
    replace_option = st.sidebar.radio(
        "Replace with empty values",
        ("Do not replace with empty values", "Replace with empty values"),
        index=0
    )

    # Determine if replacement should occur
    replace_with_empty = replace_option == "Replace with empty values"

    # Display information if both files are uploaded
    if old_excel and latest_excel:
        old_df = pd.read_excel(old_excel)
        latest_df = pd.read_excel(latest_excel)

        # Update entries in old_df based on latest_df
        updated_df = update_entries(old_df, latest_df, replace_with_empty=replace_with_empty)

        st.subheader("Updated Data")
        st.dataframe(updated_df, use_container_width=True)

        # Option to download the updated DataFrame as an Excel file
        download_excel(updated_df, "updated_data.xlsx")

    elif not old_excel:
        st.info("Please upload the Old Excel file.")
    elif not latest_excel:
        st.info("Please upload the Latest Excel file.")
