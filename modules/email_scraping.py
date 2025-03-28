import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import validators
from io import BytesIO  # For in-memory file handling
import streamlit as st

# Function to extract email addresses from page content
def extract_emails(soup):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return list(set(re.findall(email_regex, soup.get_text())))

# Function to scrape emails with user-provided keywords
def scrape_emails_with_keywords(base_url, keywords, results_df):
    contact_info = {'url': base_url, 'emails': []}

    try:
        st.write(f"Visiting main page: {base_url}")
        response = requests.get(base_url)
        if response.status_code != 200:
            st.write(f"Failed to fetch {base_url}. Status Code: {response.status_code}")
            return results_df

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract emails from the homepage
        homepage_emails = extract_emails(soup)
        contact_info['emails'].extend(homepage_emails)

        # Look for pages containing user-specified keywords
        keyword_links = []
        for a_tag in soup.find_all('a', href=True):
            if any(keyword in a_tag.text.lower() or keyword in a_tag['href'].lower() for keyword in keywords):
                keyword_links.append(a_tag['href'])

        # Scrape emails from pages that match the keywords
        for link in keyword_links:
            contact_url = link if link.startswith("http") else base_url.rstrip("/") + "/" + link.lstrip("/")
            st.write(f"Visiting page: {contact_url}")
            response = requests.get(contact_url)
            if response.status_code != 200:
                st.write(f"Failed to fetch {contact_url}. Status Code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            page_emails = extract_emails(soup)
            contact_info['emails'].extend(page_emails)

    except Exception as e:
        st.write(f"Error processing {base_url}: {e}")

    # Limit emails to a maximum of 5 and convert list to a comma-separated string
    contact_info['emails'] = ', '.join(list(set(contact_info['emails']))[:5])

    # Update DataFrame dynamically
    results_df = pd.concat([results_df, pd.DataFrame([contact_info])], ignore_index=True)
    st.dataframe(results_df)
    return results_df

# Streamlit interface
def render_email_scraping_page():
    st.markdown("<h2 style='text-align: center;'>Email Scraping with Real-Time Updates</h2>", unsafe_allow_html=True)

    # Button to reset the session state and the results DataFrame
    if st.button('Reset Database'):
        st.session_state.results_df = pd.DataFrame(columns=["url", "emails"])
        st.write("Database has been reset.")

    # Text input for custom keywords
    keyword_input = st.text_input("Enter keywords to search (comma-separated):", value="contact, about, support")
    keywords = [kw.strip().lower() for kw in keyword_input.split(",")]

    # File uploader for input file
    uploaded_file = st.file_uploader("Upload an Excel File with URLs", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        if "URL" not in df.columns:
            st.error("The uploaded file must have a column named 'URL'.")
            return

        company_urls = df["URL"].tolist()

        # Initialize results DataFrame if it doesn't exist in session state
        if "results_df" not in st.session_state:
            st.session_state.results_df = pd.DataFrame(columns=["url", "emails"])

        # Button to start scraping
        if st.button('Start Scraping'):
            # Process each URL and update results in real-time
            for company_url in company_urls:
                if company_url.startswith("www."):
                    company_url = "http://" + company_url  # Prepend protocol if missing

                if not validators.url(company_url):
                    st.write(f"Skipping invalid URL: {company_url}")
                    continue

                st.write(f"Scraping {company_url} with keywords: {keywords}")
                st.session_state.results_df = scrape_emails_with_keywords(company_url, keywords, st.session_state.results_df)

            # Save the real-time results to a BytesIO object (in-memory file)
            excel_buffer = BytesIO()
            st.session_state.results_df.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)  # Move cursor to the beginning of the buffer

            # Provide a download button for the file
            st.download_button(
                label="Download Results as Excel",
                data=excel_buffer,
                file_name="real_time_email_info.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Run the Streamlit app
if __name__ == "__main__":
    render_email_scraping_page()
