import streamlit as st
from modules.data_query import render_data_query_dashboard
from modules.update_entries import render_update_entries_page
from modules.fuzzy_lookup import render_fuzzy_lookup_page  # Import the fuzzy lookup page
from modules.html_scraping import render_html_scraping_page
from modules.email_scraping import render_email_scraping_page
from utils.ui_utils import set_logo_and_links
from modules.check_page import render_check_page
from modules.python_html_scraping import render_python_html_scraping_page

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

# Hardcoded user credentials (for demonstration purposes)
USER_CREDENTIALS = {
    "admin": "admin1234",
    "user": "eupdgroup"
}

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.sidebar.success(f"Welcome, {username}!")
            st.rerun()  # Force page rerun after login
        else:
            st.sidebar.error("Invalid username or password.")

def logout():
    st.session_state["authenticated"] = False
    st.session_state.pop("username", None)
    st.sidebar.success("You have been logged out.")
    st.rerun()  # Force page rerun after logout

def main():
    # Initialize session state variables
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()
    else:
        set_logo_and_links()
        st.sidebar.title("Navigation")
        st.sidebar.button("Logout", on_click=logout)

        page_selection = st.sidebar.selectbox(
            "Function",
            ["HTML Scraping", "Email Scraping", "Python HTML Scraping", "Fuzzy Lookup", "Update Excel Entries", "Dynamic Excel Data Query", "Check and Replace"],
            index=0
        )

        if page_selection == "Fuzzy Lookup":
            st.markdown("<h2 style='text-align: center;'>Fuzzy Lookup</h2>", unsafe_allow_html=True)
            render_fuzzy_lookup_page()
        elif page_selection == "Update Excel Entries":
            st.markdown("<h2 style='text-align: center;'>Update Entries</h2>", unsafe_allow_html=True)
            render_update_entries_page()
        elif page_selection == "Dynamic Excel Data Query":
            st.markdown("<h2 style='text-align: center;'>Dynamic Excel Data Query Dashboard</h2>", unsafe_allow_html=True)
            render_data_query_dashboard()
        elif page_selection == "Check and Replace":
            render_check_page()
        elif page_selection == "HTML Scraping":
            render_html_scraping_page()
        elif page_selection == "Email Scraping":
            render_email_scraping_page()
        elif page_selection == "Python HTML Scraping":
            st.markdown("<h2 style='text-align: center;'>Python HTML Scraping</h2>", unsafe_allow_html=True)
            render_python_html_scraping_page()
        
        # Add support text at the bottom
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            """
            <p style='text-align: center; font-size: 14px;'>
            Facing any problems or need support? 
            Contact : Yash Gandhi - y.gandhi@eupd-research.com         </p>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
