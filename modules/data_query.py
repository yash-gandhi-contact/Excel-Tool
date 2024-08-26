import streamlit as st
from utils.data_utils import clean_data, filter_dataframe 
from utils.file_utils import read_files
from utils.ui_utils import apply_styling

def render_data_query_dashboard():
    uploaded_files = st.sidebar.file_uploader(
        "Upload your files", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True
    )
    if uploaded_files:
        combined_df = read_files(uploaded_files)
        
        if combined_df.empty:
            st.warning("No valid data could be read from the uploaded files.")
            return

        # Allow the user to select the index column
        st.sidebar.subheader("Select Index Column")
        index_column = st.sidebar.selectbox(
            "Choose the index column:",
            options=combined_df.columns.tolist(),
            index=0
        )

        # Set the selected column as the index
        combined_df.set_index(index_column, inplace=True)

        # Clean and ensure consistent data types
        cleaned_df = clean_data(combined_df)

        st.sidebar.title("Filter Options")
        filtered_data = filter_dataframe(cleaned_df)

        st.subheader("Filtered Data")
        st.dataframe(filtered_data, use_container_width=True)
        apply_styling()

    else:
        st.info("Please upload one or more Excel or CSV files to get started.")
