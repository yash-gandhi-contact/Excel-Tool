# # import streamlit as st
# # import pandas as pd
# # import requests
# # from bs4 import BeautifulSoup

# # def scrape_product_data_from_urls(uploaded_file, tag, attribute, class_name):
# #     # Load URLs from the uploaded Excel file
# #     df_urls = pd.read_excel(uploaded_file)
    
# #     url_column_name = 'URL'
# #     if url_column_name not in df_urls.columns:
# #         st.error(f"Column '{url_column_name}' not found in the uploaded file.")
# #         return pd.DataFrame()

# #     all_data = []

# #     for url in df_urls[url_column_name]:
# #         st.write(f"Scraping URL: {url}")
# #         try:
# #             response = requests.get(url, timeout=10)
# #             response.raise_for_status()  # Raise an error for bad status codes
# #             soup = BeautifulSoup(response.content, 'html.parser')

# #             # Extract user-specified data
# #             if tag:
# #                 if attribute and class_name:
# #                     element = soup.find(tag, {attribute: class_name})
# #                 elif attribute:
# #                     element = soup.find(tag, {attribute: True})
# #                 else:
# #                     element = soup.find(tag)
                
# #                 extracted_text = element.text.strip() if element else "Not Found"
# #             else:
# #                 extracted_text = "No tag specified"

# #             # Store the data
# #             data = {'URL': url, 'Extracted Data': extracted_text}
# #             all_data.append(data)

# #         except requests.exceptions.RequestException as e:
# #             st.error(f"Error fetching {url}: {e}")

# #     return pd.DataFrame(all_data)

# # def render_python_html_scraping_page():
# #     st.title("Python HTML Scraping")

# #     uploaded_file = st.file_uploader("Upload an Excel file containing URLs", type=["xlsx"])

# #     st.write("### Enter Parameters for HTML Extraction")
# #     tag = st.text_input("Tag (e.g., h1, div, span)", value="h1")
# #     attribute = st.text_input("Attribute (e.g., class, id)", value="class")
# #     class_name = st.text_input("Class/ID Name (optional)", value="product-title")

# #     if uploaded_file and st.button("Start Scraping"):
# #         df_scraped = scrape_product_data_from_urls(uploaded_file, tag, attribute, class_name)

# #         if not df_scraped.empty:
# #             st.write("### Scraped Data")
# #             st.dataframe(df_scraped)

# #             # Provide download link
# #             csv = df_scraped.to_csv(index=False).encode('utf-8')
# #             st.download_button("Download CSV", csv, "scraped_data.csv", "text/csv", key="download_csv")


# import streamlit as st
# import pandas as pd
# import requests
# from bs4 import BeautifulSoup

# def scrape_product_data_from_urls(uploaded_file, tag_attr_class_pairs, column_names):
#     # Load URLs from the uploaded Excel file
#     df_urls = pd.read_excel(uploaded_file)
    
#     url_column_name = 'URL'
#     if url_column_name not in df_urls.columns:
#         st.error(f"Column '{url_column_name}' not found in the uploaded file.")
#         return pd.DataFrame()

#     all_data = []

#     for url in df_urls[url_column_name]:
#         st.write(f"Scraping URL: {url}")
#         row_data = {'URL': url}
#         try:
#             response = requests.get(url, timeout=10)
#             response.raise_for_status()  # Raise an error for bad status codes
#             soup = BeautifulSoup(response.content, 'html.parser')

#             # Loop through each pair of tag, attribute, class_name
#             for idx, (tag, attribute, class_name) in enumerate(tag_attr_class_pairs):
#                 if tag:
#                     if attribute and class_name:
#                         element = soup.find(tag, {attribute: class_name})
#                     elif attribute:
#                         element = soup.find(tag, {attribute: True})
#                     else:
#                         element = soup.find(tag)

#                     extracted_text = element.text.strip() if element else "Not Found"
#                 else:
#                     extracted_text = "No tag specified"
                
#                 # Store the data in the corresponding column for the current set
#                 row_data[column_names[idx]] = extracted_text

#             all_data.append(row_data)

#         except requests.exceptions.RequestException as e:
#             st.error(f"Error fetching {url}: {e}")

#     return pd.DataFrame(all_data)

# def render_python_html_scraping_page():
#     st.title("Python HTML Scraping")

#     # Reset button functionality (clear session state)
#     if st.button("Reset"):
#         st.session_state.uploaded_file = None
#         st.session_state.tag_attr_class_pairs = []
#         st.session_state.column_names = []

#     uploaded_file = st.file_uploader("Upload an Excel file containing URLs", type=["xlsx"])

#     # Save uploaded file in session state
#     if uploaded_file is not None:
#         st.session_state.uploaded_file = uploaded_file

#     st.write("### Enter Parameters for HTML Extraction")

#     # Dropdown to select the number of tag-attribute-class sets (up to 6)
#     num_sets = st.selectbox("How many sets of parameters do you want to provide?", [1, 2, 3, 4, 5, 6])

#     tag_attr_class_pairs = []
#     column_names = []

#     for i in range(num_sets):
#         st.write(f"### Set {i + 1}")

#         # Custom input for tag
#         tag = st.text_input(f"Tag {i + 1} (e.g., h1, div, span, p, img, li, section)", value="h1")

#         # Custom input for attribute
#         attribute = st.text_input(f"Attribute {i + 1} (e.g., class, id, name, href, src)", value="class")

#         # Custom input for class or ID name
#         class_name = st.text_input(f"Class/ID Name {i + 1} (optional, e.g., product-title)", value="")

#         tag_attr_class_pairs.append((tag, attribute, class_name))

#         # Custom input for column name
#         column_name = st.text_input(f"Column Name for Set {i + 1} (e.g., Product Title, Description, Price)", value=f"Set {i + 1}")
#         column_names.append(column_name)

#     # Save parameters to session state
#     st.session_state.tag_attr_class_pairs = tag_attr_class_pairs
#     st.session_state.column_names = column_names

#     if uploaded_file and st.button("Start Scraping"):
#         df_scraped = scrape_product_data_from_urls(uploaded_file, tag_attr_class_pairs, column_names)

#         if not df_scraped.empty:
#             st.write("### Scraped Data")
#             st.dataframe(df_scraped)

#             # Provide download link
#             csv = df_scraped.to_csv(index=False).encode('utf-8')
#             st.download_button("Download CSV", csv, "scraped_data.csv", "text/csv", key="download_csv")

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup


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
    df_urls = pd.read_excel(uploaded_file)

    url_column_name = "URL"
    if url_column_name not in df_urls.columns:
        st.error(f"Column '{url_column_name}' not found in the uploaded file.")
        return pd.DataFrame()

    all_data = []

    for url in df_urls[url_column_name]:
        st.write(f"Scraping URL: {url}")
        row_data = {"URL": url}
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise error for bad status codes
            soup = BeautifulSoup(response.content, "html.parser")

            # Loop through the specified tag-attribute-class combinations
            for idx, (tag, attribute, class_name) in enumerate(tag_attr_class_pairs):
                if tag:
                    # Dynamically find elements based on attribute and class
                    if attribute and class_name:
                        elements = soup.find_all(tag, {attribute: class_name})
                    elif attribute:
                        elements = soup.find_all(tag, {attribute: True})
                    else:
                        elements = soup.find_all(tag)

                    extracted_text = []
                    for element in elements:
                        # If child elements are specified, extract only from them
                        if child_elements:
                            child_texts = [
                                child.text.strip()
                                for child_tag in child_elements
                                for child in element.find_all(child_tag)
                                if child.text.strip()
                            ]
                            extracted_text.extend(child_texts)
                        else:
                            # Get all text if no child elements specified
                            extracted_text.append(element.get_text(strip=True))

                    # Store the extracted data in the corresponding column
                    row_data[column_names[idx]] = "; ".join(extracted_text) if extracted_text else "Not Found"
                else:
                    row_data[column_names[idx]] = "No tag specified"

            all_data.append(row_data)

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching {url}: {e}")
            for column_name in column_names:
                row_data[column_name] = "Error"

            all_data.append(row_data)

    return pd.DataFrame(all_data)


def render_python_html_scraping_page():
    st.title("Python HTML Scraping")

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

        tag = st.text_input(f"Tag {i + 1} (e.g., h1, div, span, li)", value="h1")
        attribute = st.text_input(f"Attribute {i + 1} (e.g., class, id, name)", value="class")
        class_name = st.text_input(f"Class/ID Name {i + 1} (optional)", value="")
        tag_attr_class_pairs.append((tag, attribute, class_name))

        column_name = st.text_input(f"Column Name for Set {i + 1} (e.g., Product Title, Price)", value=f"Set {i + 1}")
        column_names.append(column_name)

    st.write("### Optional Child Tags")
    child_elements = st.multiselect(
        "Specify child tags for extraction (leave blank for all text within the main tag)",
<<<<<<< HEAD
        options=["th", "td", "span", "div", "p", "h3", "li", "ui"],
=======
        options=["th", "td", "span", "div", "p", "h3", "li"],
>>>>>>> 
    )

    st.session_state.tag_attr_class_pairs = tag_attr_class_pairs
    st.session_state.column_names = column_names

    if uploaded_file and st.button("Start Scraping"):
        df_scraped = scrape_product_data_from_urls(
            uploaded_file, tag_attr_class_pairs, column_names, child_elements
        )

        if not df_scraped.empty:
            st.write("### Scraped Data")
            st.dataframe(df_scraped)

            csv = df_scraped.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "scraped_data.csv", "text/csv", key="download_csv")


if __name__ == "__main__":
    render_python_html_scraping_page()
<<<<<<< HEAD





=======
>>>>>>> 5c38d1321a0feebbb77cb4461de0e598dc5288df
