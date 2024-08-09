import streamlit as st

def set_logo_and_links():
    logo_url = "https://www.eupd-research.com/wp-content/uploads/2019/09/Logo_EuPD_Research_RGB.png"
    linkedin_logo_url = "https://cdn-icons-png.flaticon.com/512/174/174857.png"
    st.sidebar.image(logo_url, width=200)
    st.sidebar.markdown(f"""
        <div style='text-align: left; margin-top: 6px;'>
            <small>Made by Yash Gandhi</small><br>
            <a href='https://www.linkedin.com/in/yash--gandhi/' target='_blank'>
                <img src='{linkedin_logo_url}' alt='LinkedIn Profile' style='width: 20px; height: 20px;'>
            </a>
        </div>
    """, unsafe_allow_html=True)

def apply_styling():
    st.markdown("""
        <style>
        .dataframe tbody tr:hover {
            background-color: #f5f5f5;
        }
        .dataframe thead th {
            background-color: #007bff;
            color: white;
        }
        .dataframe td, .dataframe th {
            text-align: center;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
 
