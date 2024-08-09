import streamlit as st
from pages.data_query import render_data_query_dashboard
from pages.update_entries import render_update_entries_page
from utils.ui_utils import set_logo_and_links
from pages.update_entries import render_update_entries_page
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))

# Set page configuration
st.set_page_config(
    page_title="EUPD Excel-Tool",  # Title of the app in the browser tab
    page_icon="📊",                 # Icon to display in the browser tab
    layout="wide",                  # Use a wide layout for the app
    initial_sidebar_state="expanded" # Sidebar state
)

def main():
    set_logo_and_links()
    st.sidebar.title("Navigation")
    page_selection = st.sidebar.selectbox(
        "Select Page",
        ["Update Entries", "Dynamic Excel Data Query"],
        index=0
    )
    if page_selection == "Dynamic Excel Data Query":
        st.markdown("<h2 style='text-align: center;'>Dynamic Excel Data Query Dashboard</h2>", unsafe_allow_html=True)
        render_data_query_dashboard()
    elif page_selection == "Update Entries":
        st.markdown("<h2 style='text-align: center;'>Update Entries</h2>", unsafe_allow_html=True)
        render_update_entries_page()

if __name__ == "__main__":
    main()
