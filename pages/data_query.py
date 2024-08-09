import streamlit as st
from utils.data_utils import clean_data, filter_dataframe, extract_alphabetic_prefix
from utils.file_utils import read_excel_files
from utils.ui_utils import apply_styling

def render_data_query_dashboard():
    uploaded_files = st.sidebar.file_uploader("Upload your Excel files", type=['xlsx', 'xls'], accept_multiple_files=True)
    if uploaded_files:
        combined_df = read_excel_files(uploaded_files)
        cleaned_df = clean_data(combined_df)

        if 'ID' in cleaned_df.columns:
            cleaned_df['ID_prefix'] = cleaned_df['ID'].apply(extract_alphabetic_prefix)
            id_prefixes = cleaned_df['ID_prefix'].dropna().unique()
            selected_prefix = st.sidebar.selectbox("Select ID Prefix", options=['All'] + list(id_prefixes))
            if selected_prefix != 'All':
                cleaned_df = cleaned_df[cleaned_df['ID_prefix'] == selected_prefix]

        st.sidebar.title("Filter Options")
        filtered_data = filter_dataframe(cleaned_df)

        st.subheader("Filtered Data")
        st.dataframe(filtered_data, use_container_width=True)
        apply_styling()

    else:
        st.info("Please upload one or more Excel files to get started.")
