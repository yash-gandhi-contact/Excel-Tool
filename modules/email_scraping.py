import requests
from bs4 import BeautifulSoup
import re
import time
import validators
import pandas as pd
import streamlit as st
from io import BytesIO
from requests.exceptions import SSLError, RequestException

# Function to extract email addresses from page content
def extract_emails(soup):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA0-9.-]+\.[a-zA-Z]{2,}'
    return list(set(re.findall(email_regex, soup.get_text())))

# Function to scrape emails from specific pages with keywords
def scrape_emails_with_keywords(base_url, keywords, results_df, log_expander, progress_bar, total_urls):
    contact_info = {'url': base_url, 'emails': []}

    try:
        with log_expander:
            st.write(f"Visiting main page: {base_url}")

        # Adding a 5-second delay before scraping the main URL
        time.sleep(5)

        response = requests.get(base_url, timeout=10)

        if response.status_code != 200:
            with log_expander:
                st.write(f"Failed to fetch {base_url}. Status Code: {response.status_code}")
            contact_info['emails'] = ''  # No emails found, empty list
            results_df = pd.concat([results_df, pd.DataFrame([contact_info])], ignore_index=True)
            return results_df

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract emails from the homepage
        homepage_emails = extract_emails(soup)
        contact_info['emails'].extend(homepage_emails)

        # Look for pages containing user-specified keywords in their URL or content
        keyword_links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            if any(keyword in link.lower() for keyword in keywords):
                full_url = link if link.startswith("http") else base_url.rstrip("/") + "/" + link.lstrip("/")
                keyword_links.append(full_url)

        # Scrape emails only from keyword-matching pages
        for contact_url in keyword_links:
            with log_expander:
                st.write(f"Visiting page: {contact_url}")
            try:
                response = requests.get(contact_url, timeout=10)
                if response.status_code != 200:
                    with log_expander:
                        st.write(f"Failed to fetch {contact_url}. Status Code: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                page_emails = extract_emails(soup)
                contact_info['emails'].extend(page_emails)
            except (SSLError, RequestException) as e:
                with log_expander:
                    st.write(f"Error processing {contact_url}: {e}. Skipping this page.")
                continue

    except (SSLError, RequestException) as e:
        with log_expander:
            st.write(f"Error processing {base_url}: {e}. Skipping this URL.")
        contact_info['emails'] = ''  # No emails found, empty list
        results_df = pd.concat([results_df, pd.DataFrame([contact_info])], ignore_index=True)
        return results_df

    # Limit emails to a maximum of 5 and convert list to a comma-separated string
    contact_info['emails'] = ', '.join(list(set(contact_info['emails']))[:5]) if contact_info['emails'] else ''

    # Update DataFrame dynamically
    results_df = pd.concat([results_df, pd.DataFrame([contact_info])], ignore_index=True)
    st.dataframe(results_df)

    # Update progress bar
    progress_value = int((results_df.shape[0] / total_urls) * 100)  # Calculate the percentage
    progress_bar.progress(progress_value)

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

        # Add an expander for the log messages
        log_expander = st.expander("Logs", expanded=False)

        # Add progress bar to show completion of URLs
        progress_bar = st.progress(0)

        # Button to start scraping
        if st.button('Start Scraping'):
            total_urls = len(company_urls)  # Get the total number of URLs
            # Process each URL and update results in real-time
            for company_url in company_urls:
                if company_url.startswith("www."):
                    company_url = "http://" + company_url  # Prepend protocol if missing

                if not validators.url(company_url):
                    st.write(f"Skipping invalid URL: {company_url}")
                    continue

                st.write(f"Scraping {company_url} with keywords: {keywords}")
                st.session_state.results_df = scrape_emails_with_keywords(company_url, keywords, st.session_state.results_df, log_expander, progress_bar, total_urls)

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
