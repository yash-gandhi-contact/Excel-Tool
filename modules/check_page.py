import streamlit as st
import pandas as pd
from io import BytesIO
from utils.file_utils import read_files

def download_as_excel(master_data_df):
    """Converts the master data dataframe into an Excel file with one sheet."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        master_data_df.to_excel(writer, sheet_name='Updated Master Data', index=False)
    output.seek(0)
    return output

def render_check_page():
    st.header("Check and Replace")

    # File uploaders in the sidebar
    st.sidebar.header("Upload Files")
    new_data_file = st.sidebar.file_uploader("Upload New Data", type=['csv', 'xlsx', 'xls'], key="new_data")
    master_data_file = st.sidebar.file_uploader("Upload Master Data", type=['csv', 'xlsx', 'xls'], key="master_data")

    # Initialize dataframes
    new_data_df = pd.DataFrame()
    master_data_df = pd.DataFrame()
    new_data_sheets = []
    master_data_sheets = []

    # Load data if files are uploaded
    if new_data_file:
        new_data_df, new_data_sheets = read_files([new_data_file])

    if master_data_file:
        master_data_df, master_data_sheets = read_files([master_data_file])

    # Display sheet selection for New Data and Master Data
    if new_data_sheets or master_data_sheets:
        st.subheader("Select Sheet")
        
        # Sheet selection for New Data
        if new_data_sheets:
            new_data_sheet = st.selectbox("Select Sheet for New Data", new_data_sheets)
            if new_data_sheet:
                new_data_df = pd.read_excel(new_data_file, sheet_name=new_data_sheet)
        
        # Sheet selection for Master Data
        if master_data_sheets:
            master_data_sheet = st.selectbox("Select Sheet for Master Data", master_data_sheets)
            if master_data_sheet:
                master_data_df = pd.read_excel(master_data_file, sheet_name=master_data_sheet)

    # Display dropdowns for column selection if dataframes are loaded
    if not new_data_df.empty and not master_data_df.empty:
        st.subheader("Select Columns")

        new_data_columns = new_data_df.columns.tolist()
        master_data_columns = master_data_df.columns.tolist()

        # Place dropdowns in a single line
        col1, col2 = st.columns(2)
        with col1:
            selected_new_column = st.selectbox("Select column from New Data as Primary Key", new_data_columns)
        with col2:
            selected_master_column = st.selectbox("Select column from Master Data as Primary Key", master_data_columns)

        st.write("You selected:")
        st.write(f"New Data Primary Key Column: {selected_new_column}")
        st.write(f"Master Data Primary Key Column: {selected_master_column}")

        # New subheader for comparing columns
        st.subheader("Compare Columns")

        # Dropdowns for comparison
        col3, col4 = st.columns(2)
        with col3:
            compare_new_column = st.selectbox("Select column from New Data for comparison", new_data_columns)
        with col4:
            compare_master_column = st.selectbox("Select column from Master Data for comparison", master_data_columns)

        st.write("You selected for comparison:")
        st.write(f"New Data Column: {compare_new_column}")
        st.write(f"Master Data Column: {compare_master_column}")

        # Radio buttons for replacement option
        replace_option = st.radio("Choose how to handle empty/NaN values", 
                                   ("Replace with empty or NaN values", "Replace without empty or NaN values"))

        replace_with_empty = replace_option == "Replace with empty or NaN values"

        # Comparison based on primary keys
        if st.button("Compare"):
            # Merge dataframes on primary keys
            merged_df = pd.merge(new_data_df[[selected_new_column, compare_new_column]], 
                                  master_data_df[[selected_master_column, compare_master_column]], 
                                  left_on=selected_new_column, 
                                  right_on=selected_master_column, 
                                  how='outer', 
                                  suffixes=('_new', '_master'))

            # Adding the result column with comparison
            def compare_and_replace(row):
                if pd.isna(row[f"{compare_new_column}_new"]):  # If new data is empty
                    if replace_with_empty:
                        return pd.NA  # Replace with NaN if allowed
                    else:
                        return row[f"{compare_master_column}_master"]  # Keep the old value
                return row[f"{compare_new_column}_new"]  # Replace with the new value otherwise

            # Apply the replacement logic
            merged_df['Comparison_Result'] = merged_df.apply(compare_and_replace, axis=1)

            st.subheader("Comparison Results")
            st.dataframe(merged_df)

            # Create a new dataframe reflecting changes in Master Data
            updated_master_data_df = master_data_df.copy()
            for index, row in merged_df.iterrows():
                master_index = updated_master_data_df[updated_master_data_df[selected_master_column] == row[selected_master_column]].index
                if not master_index.empty:
                    updated_master_data_df.loc[master_index, compare_master_column] = row['Comparison_Result']

            st.subheader("Updated Master Data")
            st.dataframe(updated_master_data_df)

            # Button to download the updated master data
            st.download_button(
                label="Download Updated Master Data",
                data=download_as_excel(updated_master_data_df),
                file_name='updated_master_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    else:
        st.info("Please upload both New Data and Master Data files to see the columns.")

if __name__ == "__main__":
    render_check_page()
