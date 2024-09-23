import streamlit as st
from modules.data_query import render_data_query_dashboard
from modules.update_entries import render_update_entries_page
from modules.fuzzy_lookup import render_fuzzy_lookup_page  # Import the fuzzy lookup page
from utils.ui_utils import set_logo_and_links
from modules.check_page import render_check_page

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))

# Set page configuration
st.set_page_config(
    page_title="EUPD Excel-Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    set_logo_and_links()
    st.sidebar.title("Navigation")
    page_selection = st.sidebar.selectbox(
        "Select Page",
        ["Update Entries", "Dynamic Excel Data Query", "Fuzzy Lookup", "Check and Replace"],  # Add "Check" to the list
        index=0
    )
    if page_selection == "Dynamic Excel Data Query":
        st.markdown("<h2 style='text-align: center;'>Dynamic Excel Data Query Dashboard</h2>", unsafe_allow_html=True)
        render_data_query_dashboard()
    elif page_selection == "Update Entries":
        st.markdown("<h2 style='text-align: center;'>Update Entries</h2>", unsafe_allow_html=True)
        render_update_entries_page()
    elif page_selection == "Fuzzy Lookup":  # Call the render function for the fuzzy lookup page
        st.markdown("<h2 style='text-align: center;'>Fuzzy Lookup</h2>", unsafe_allow_html=True)
        render_fuzzy_lookup_page()
    elif page_selection == "Check and Replace":  # New empty Check page
        
        render_check_page()

if __name__ == "__main__":
    main()
