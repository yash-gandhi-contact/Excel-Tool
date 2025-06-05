import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from io import BytesIO
from datetime import datetime
from time import sleep

# Initialize session state attributes if not already set
def initialize_session_state():
    if "df1" not in st.session_state:
        st.session_state.df1 = pd.DataFrame()
    if "df2" not in st.session_state:
        st.session_state.df2 = pd.DataFrame()
    if "fuzzy_results" not in st.session_state:
        st.session_state.fuzzy_results = pd.DataFrame()
    if "filtered_results" not in st.session_state:
        st.session_state.filtered_results = pd.DataFrame()
    if "duplicate_values" not in st.session_state:
        st.session_state.duplicate_values = pd.DataFrame()
    if "column_pairs" not in st.session_state:
        st.session_state.column_pairs = []
    if "thresholds" not in st.session_state:
        st.session_state.thresholds = {}


# Call the initialization function on app start
initialize_session_state()
def ensure_unique_columns(df):
    """Ensure all column names are unique."""
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df

def fuzzy_match_columns(df1, df2, col1, col2, progress_bar=None):
    """Apply fuzzy matching between two columns and return similarity scores, matched values, and original compared values."""
    similarity_scores = []
    matched_values = []
    compared_values = []

    for i, x in enumerate(df1[col1]):
        best_match = max(df2[col2], key=lambda y: fuzz.ratio(str(x), str(y)))
        similarity_score = fuzz.ratio(str(x), str(best_match))
        similarity_scores.append(similarity_score)
        matched_values.append(best_match)
        compared_values.append(x)  # Keep the original value being compared
        
        # Update the progress bar if provided
        if progress_bar:
            progress_bar.progress((i + 1) / len(df1[col1]))
        sleep(0.05)  # Optional: Simulate delay for visual effect

    return similarity_scores, matched_values, compared_values

def render_fuzzy_lookup_page():   
    st.warning("Use this button after uploading a new files!" , icon="⚠️")       
    if st.button("Reset"):
        # Clear session state related to the uploaded files
            initialize_session_state()
            st.session_state.df1 = pd.DataFrame()
            st.session_state.df2 = pd.DataFrame()
            st.session_state.fuzzy_results = pd.DataFrame()
            st.session_state.filtered_results = pd.DataFrame()
            st.session_state.duplicate_values = pd.DataFrame()
            st.session_state.column_pairs = []
            st.session_state.thresholds = {}

            for i in range(5):  # Adjust the range based on the maximum number of pairs allowed
                if f"col1_{i}" in st.session_state:
                    del st.session_state[f"col1_{i}"]
                if f"col2_{i}" in st.session_state:
                    del st.session_state[f"col2_{i}"]
            st.success("Files reset! Please upload new files.")    
    
    col1, col2 = st.columns(2)
    with col1:
        df1_file = st.file_uploader("Upload New Data File", type=['xlsx', 'csv'], key="upload1")
    with col2:
        df2_file = st.file_uploader("Upload Main Data File", type=['xlsx', 'csv'], key="upload2")

    # Function to reload data based on sheet selection
    def reload_sheet_data(df_file, selected_sheet, is_excel):
        if is_excel:
            return pd.read_excel(df_file, sheet_name=selected_sheet)
        else:
            return pd.read_csv(df_file)

    # Sheet selection logic and data reloading
    if df1_file and df2_file:
        if df1_file.name.endswith('xlsx') and df2_file.name.endswith('xlsx'):
            all_sheets1 = pd.ExcelFile(df1_file).sheet_names
            all_sheets2 = pd.ExcelFile(df2_file).sheet_names

            col1, col2 = st.columns(2)
            with col1:
                st.session_state.selected_sheet1 = st.selectbox(
                    "Select Sheet for File 1",
                    all_sheets1,
                    key="sheet_selector_1"
                )
                st.session_state.df1 = reload_sheet_data(df1_file, st.session_state.selected_sheet1, is_excel=True)
            with col2:
                st.session_state.selected_sheet2 = st.selectbox(
                    "Select Sheet for File 2",
                    all_sheets2,
                    key="sheet_selector_2"
                )
                st.session_state.df2 = reload_sheet_data(df2_file, st.session_state.selected_sheet2, is_excel=True)
        else:
            st.session_state.df1 = reload_sheet_data(df1_file, None, is_excel=False)
            st.session_state.df2 = reload_sheet_data(df2_file, None, is_excel=False)

        
    
    if not st.session_state.df1.empty and not st.session_state.df2.empty:
        
            st.write("Select Columns to Compare")
            num_pairs = st.slider("Select number of column pairs to compare", 1, 5, 1)
            col_pairs = []
            with st.form("fuzzy_form"):
                for i in range(num_pairs):
                    col1, col2 = st.columns(2)  # Create two columns for layout
                    with col1:
                        col1_selection = st.selectbox(
                            f"Select column {i + 1} from Master Data",
                            st.session_state.df1.columns,
                            key=f"col1_{i}"
                        )
                    with col2:
                        col2_selection = st.selectbox(
                            f"Select column {i + 1} from New Data",
                            st.session_state.df2.columns,
                            key=f"col2_{i}"
                        )
                    col_pairs.append((col1_selection, col2_selection))  # Store selected columns as pairs

                compare_button = st.form_submit_button("Compare Columns")

            if compare_button:
                all_similarity_scores = []
                all_matched_values = []
                all_original_values = []
                similarity_columns = []

                progress_message = st.empty()  # Display a message for progress
                progress_bar = st.progress(0)  # Initialize progress bar

                
                for col1, col2 in col_pairs:
                    # Display the processing message
                    progress_message.write(f"Processing fuzzy matching for {col1} and {col2}...")
                    
                    # Update the call to fuzzy_match_columns with the progress bar
                    similarity_scores, matched_values, original_values = fuzzy_match_columns(
                        st.session_state.df1, st.session_state.df2, col1, col2, progress_bar
                    )

                    similarity_col = f"{col1}-{col2} Similarity %"
                    match_col = f"Best Match in {col2}"
                    original_col = f"Original {col1}"  # Column for original values being compared

                    similarity_df = st.session_state.df1.copy()
                    similarity_df[similarity_col] = similarity_scores
                    similarity_df[match_col] = matched_values
                    similarity_df[original_col] = original_values

                    # Append the group of columns in the desired order
                    all_similarity_scores.append(similarity_df[[similarity_col, match_col, original_col]])

                # Clear the progress message and bar once the processing is done
                progress_message.empty()
                progress_bar.empty()
                # Concatenate all similarity score dataframes
                st.session_state.fuzzy_results = pd.concat(all_similarity_scores, axis=1)
                
                # Include the original dataframe columns at the end (if desired)
                st.session_state.fuzzy_results = pd.concat([st.session_state.df1, st.session_state.fuzzy_results], axis=1)
                
                # Adjust column order to match: similarity, best match, original, then rest of df1 columns
                final_column_order = []
                for col1, col2 in col_pairs:
                    final_column_order += [f"Original {col1}", f"Best Match in {col2}",f"{col1}-{col2} Similarity %"]
                
                # Include original df1 columns last
                final_column_order += list(st.session_state.df1.columns)

                # Reorder and assign final result
                st.session_state.fuzzy_results = st.session_state.fuzzy_results[final_column_order]
                st.session_state.column_pairs = col_pairs
    
                for col1, col2 in col_pairs:
                    key = f"{col1}-{col2}"
                    if key not in st.session_state.thresholds:
                        st.session_state.thresholds[key] = 80
                # Add the checkbox for threshold filtering options
            st.write("Select threshold filtering mode:")
            threshold_mode = st.radio(
                label="Threshold Filtering Mode",
                options=["Identifies rows exceeding any threshold", "Identifies rows exceeding all thresholds"],
                index=0,  # Default to "any threshold"
        )

            if not st.session_state.fuzzy_results.empty:
                st.write("Master Results")
                st.write(st.session_state.fuzzy_results)

                for col1, col2 in st.session_state.column_pairs:
                    st.subheader(f"Filter Results by Similarity % for {col1}-{col2}")
                    similarity_col = f"{col1}-{col2} Similarity %"
                    threshold = st.slider(f"Set similarity threshold for {col1}-{col2}", 0, 100, st.session_state.thresholds.get(f"{col1}-{col2}", 80), key=f"threshold_{col1}_{col2}")
                    st.session_state.thresholds[f"{col1}-{col2}"] = threshold

                filter_condition = True
                duplicate_condition_any = False
                duplicate_condition_all = True

                for col1, col2 in st.session_state.column_pairs:
                    similarity_col = f"{col1}-{col2} Similarity %"
                    threshold = st.session_state.thresholds[f"{col1}-{col2}"]
                    
                    # Filter for rows below the threshold
                    filter_condition &= st.session_state.fuzzy_results[similarity_col] < threshold
                    
                    # Duplicate logic for "any" threshold mode
                    duplicate_condition_any |= st.session_state.fuzzy_results[similarity_col] >= threshold
                    
                    # Duplicate logic for "all" threshold mode
                    duplicate_condition_all &= st.session_state.fuzzy_results[similarity_col] >= threshold

                # Apply the selected threshold filtering mode
                if threshold_mode == "Identifies rows exceeding any threshold":
                    st.session_state.duplicate_values = st.session_state.fuzzy_results[duplicate_condition_any]
                elif threshold_mode == "Identifies rows exceeding all thresholds":
                    st.session_state.duplicate_values = st.session_state.fuzzy_results[duplicate_condition_all]

                # Filtered results
                st.session_state.filtered_results = st.session_state.fuzzy_results[filter_condition]

                # Display results
                st.subheader("Filtered Results")
                st.write(st.session_state.filtered_results)

                st.subheader("Duplicate Values")
                st.write(st.session_state.duplicate_values)


            if not st.session_state.df1.empty and not st.session_state.df2.empty:
                st.subheader("Download Results")

                # Get the date as a string in the required format
                current_date = datetime.now().strftime("%d_%m_%Y")

                # Generate a text input box for file name with a unique key
                file_name_input = st.text_input("Enter file name (Date will be added automatically)", key="file_name_input")

                def download_as_excel():
                            output = BytesIO()
                            writer = pd.ExcelWriter(output, engine='xlsxwriter')
                            st.session_state.filtered_results.to_excel(writer, sheet_name='Filtered Data', index=False)
                            st.session_state.duplicate_values.to_excel(writer, sheet_name='Duplicate Values', index=False)
                            writer.close()
                            output.seek(0)
                            return output
                # When download is requested
                if file_name_input:
                    st.download_button(
                        label="Download Excel File",
                        data=download_as_excel(),
                        file_name=f"{file_name_input}_{current_date}.xlsx",  # Use the dynamic file name here
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ) 

                        
                else:
                        st.error("Please enter a valid file name.")
            
if __name__ == "__main__":
    render_fuzzy_lookup_page()

