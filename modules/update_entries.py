import streamlit as st
from utils.file_utils import download_excel
from utils.data_utils import update_entries
import pandas as pd
import datetime

def read_files(uploaded_files):
    dataframes = []
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)  # Read CSV file
            else:
                df = pd.read_excel(uploaded_file)  # Read Excel file
            dataframes.append(df)
        except Exception as e:
            st.error(f"Error reading file {uploaded_file.name}: {str(e)}")
            continue

    if dataframes:
        # Combine all DataFrames into one if multiple files were uploaded
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df  # Ensure this is a single DataFrame
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no files were read successfully

def render_update_entries_page():
    st.sidebar.header("Update Entries")

    # Upload files for the old and latest data
    old_file = st.sidebar.file_uploader("Upload Old File", type=['csv', 'xlsx', 'xls'], accept_multiple_files=False, key='old_file')
    latest_file = st.sidebar.file_uploader("Upload Latest File", type=['csv', 'xlsx', 'xls'], accept_multiple_files=False, key='latest_file')

    if old_file and latest_file:
        # Read the old file and latest file into dataframes
        old_df = read_files([old_file])
        latest_df = read_files([latest_file])

        if old_df.empty or latest_df.empty:
            st.error("One or both of the files could not be read.")
            return

        # Allow the user to select the index column
        st.sidebar.subheader("Select Index Column")
        index_column = st.sidebar.selectbox(
            "Choose the index column for updating entries:",
            options=list(set(old_df.columns) & set(latest_df.columns)),  # Only columns present in both DataFrames
            index=0
        )

        # Radio button for replace with empty values option
        replace_option = st.sidebar.radio(
            "Replace with empty values",
            ("Do not replace with empty values", "Replace with empty values"),
            index=0
        )
        replace_with_empty = replace_option == "Replace with empty values"

        # Perform the update and allow the user to review changes
        updated_df = update_entries(old_df, latest_df, index_column, replace_with_empty=replace_with_empty)

        st.subheader("Review Updated Data")
        st.dataframe(updated_df, use_container_width=True)

        # Get original file name
        original_filename = old_file.name

        # Extract file name without extension
        file_name_without_ext = original_filename.rsplit('.', 1)[0]
        file_extension = original_filename.rsplit('.', 1)[1]

        # Input fields for user to specify name and date
        user_name = st.text_input("Enter your name", value="yash")
        user_date = st.date_input("Enter the date", value=datetime.date.today())
        formatted_date = user_date.strftime("%d%m%Y")  # Format the date

        if st.button("Generate Downloadable File"):
            # Construct new file name
            new_filename = f"{file_name_without_ext}_{user_name}_{formatted_date}.{file_extension}"
            download_excel(updated_df, new_filename)

        # Instructions for manual replacement
        st.write("""
        **To apply changes to your original file:**
        1. Download the updated file using the button above.
        2. Replace your original file with the downloaded file manually.
        """)

    else:
        if not old_file:
            st.info("Please upload the Old File.")
        if not latest_file:
            st.info("Please upload the Latest File.")
