import re
import pandas as pd
import streamlit as st

def render_html_scraping_page():
    st.markdown("<h2 style='text-align: center;'>HTML Scraping</h2>", unsafe_allow_html=True)
    
    # Input HTML content
    html_content = st.text_area("Paste HTML Content Here", height=200)
    
    # Input start and end patterns for the regex
    start_pattern = st.text_input("Enter the starting pattern for extraction (Regex)", value='<a href="')
    end_pattern = st.text_input("Enter the ending pattern for extraction (Regex)", value='" class="product-name" title="')
    
    # Input box for specifying the Excel file name
    excel_file_name = st.text_input("Enter Excel File Name", value="Extracted_Data")
    
    if st.button("Extract Data"):
        if html_content.strip():
            if start_pattern.strip() and end_pattern.strip():
                # Construct the full regex pattern using user input
                full_pattern = re.escape(start_pattern) + r"(.*?)" + re.escape(end_pattern)
                
                # Extract matches
                matches = re.findall(full_pattern, html_content)
                
                if matches:
                    # Convert matches to DataFrame
                    df = pd.DataFrame(matches, columns=["Extracted Data"])
                    
                    # Append '.xlsx' to the file name provided by the user
                    output_file = f"{excel_file_name}.xlsx"
                    
                    # Save DataFrame to Excel
                    df.to_excel(output_file, index=False, engine='openpyxl')
                    
                    st.success(f"Data extracted and saved to {output_file}")
                    st.dataframe(df)  # Display extracted data in the app
                    
                    # Download link for the Excel file
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Download Excel File",
                            data=file,
                            file_name=output_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("No matches found with the provided patterns.")
            else:
                st.error("Please provide both starting and ending patterns.")
        else:
            st.error("Please paste valid HTML content.")
