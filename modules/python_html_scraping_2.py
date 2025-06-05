
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def scrape_product_data_from_urls(uploaded_file, tag_attr_class_pairs, column_names, child_elements=None):
    """
    A dynamic scraping function that supports flexible extraction of text content
    based on tags, attributes, and classes, with optional child tag extraction.

    Parameters:
    - uploaded_file: Uploaded Excel file with a list of URLs.
    - tag_attr_class_pairs: List of tuples (tag, attribute, class_name).
    - column_names: List of column names for the output.
    - child_elements: Optional. List of child tags to extract text from.

    Returns:
    - DataFrame with scraped data.
    """
    # Load URLs from the uploaded file
    try:
        df_urls = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return pd.DataFrame()

    url_column_name = "URL"
    if url_column_name not in df_urls.columns:
        st.error(f"Column '{url_column_name}' not found in the uploaded file.")
        return pd.DataFrame()

    all_data = []

    def scrape_url(url):
        row_data = {"URL": url}
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            for idx, (tag, attribute, class_name) in enumerate(tag_attr_class_pairs):
                if not tag:
                    row_data[column_names[idx]] = "No tag specified"
                    continue

                # Dynamically find elements based on attribute and class
                if attribute and class_name:
                    elements = soup.find_all(tag, {attribute: class_name})
                elif attribute:
                    elements = soup.find_all(tag, {attribute: True})
                else:
                    elements = soup.find_all(tag)

                extracted_text = []
                for element in elements:
                    # Extract text from child elements if specified
                    if child_elements:
                        child_texts = [
                            child.text.strip()
                            for child_tag in child_elements
                            for child in element.find_all(child_tag)
                            if child.text.strip()
                        ]
                        extracted_text.extend(child_texts)
                    else:
                        extracted_text.append(element.get_text(strip=True))

                row_data[column_names[idx]] = "; ".join(extracted_text) if extracted_text else "Not Found"
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching {url}: {e}")
            for column_name in column_names:
                row_data[column_name] = "Error"
        return row_data

    with ThreadPoolExecutor() as executor:
        all_data = list(executor.map(scrape_url, df_urls[url_column_name]))

    return pd.DataFrame(all_data)


def render_python_html_scraping_page_2():
    st.title("Dynamic HTML Scraping Tool")

    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
        st.session_state.tag_attr_class_pairs = []
        st.session_state.column_names = []

    if st.button("Reset"):
        st.session_state.uploaded_file = None
        st.session_state.tag_attr_class_pairs = []
        st.session_state.column_names = []

    uploaded_file = st.file_uploader("Upload an Excel file containing URLs", type=["xlsx"])
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file

    st.write("### Enter Parameters for HTML Extraction")
    num_sets = st.selectbox("How many sets of parameters do you want to provide?", [1, 2, 3, 4, 5, 6])

    tag_attr_class_pairs = []
    column_names = []

    for i in range(num_sets):
        st.write(f"### Set {i + 1}")
        tag = st.text_input(f"Tag {i + 1} (e.g., h1, div, span, li)", key=f"tag_{i}")
        attribute = st.text_input(f"Attribute {i + 1} (e.g., class, id, name)", key=f"attribute_{i}")
        class_name = st.text_input(f"Class/ID Name {i + 1} (optional)", key=f"class_{i}")
        column_name = st.text_input(f"Column Name for Set {i + 1} (e.g., Product Title, Price)", key=f"column_{i}")

        if not column_name:
            st.error("Column name is required for each set.")
            return

        tag_attr_class_pairs.append((tag, attribute, class_name))
        column_names.append(column_name)

    st.write("### Optional Child Tags")
    child_elements = st.multiselect(
        "Specify child tags for extraction (leave blank for all text within the main tag)",
        options=["th", "td", "span", "div", "p", "h3", "li"],
        default=None,
    )

    if uploaded_file and st.button("Start Scraping"):
        with st.spinner("Scraping in progress..."):
            df_scraped = scrape_product_data_from_urls(
                uploaded_file, tag_attr_class_pairs, column_names, child_elements
            )
            if not df_scraped.empty:
                st.success("Scraping completed successfully!")
                st.dataframe(df_scraped)

                # Allow download of the scraped data
                csv_data = df_scraped.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="scraped_data.csv",
                    mime="text/csv",
                )


# Run the app
if __name__ == "__main__":
    render_python_html_scraping_page_2()

