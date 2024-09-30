import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from io import BytesIO

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

# def fuzzy_match_columns(df1, df2, col1, col2):
#     """Apply fuzzy matching between two columns."""
#     similarity_scores = df1[col1].apply(lambda x: max([fuzz.ratio(str(x), str(y)) for y in df2[col2]], default=0))
#     return similarity_scores


# def render_fuzzy_lookup_page():   
        
#     if st.button("Reset"):
#         # Clear session state related to the uploaded files
#             initialize_session_state()
#             st.session_state.df1 = pd.DataFrame()
#             st.session_state.df2 = pd.DataFrame()
#             st.session_state.fuzzy_results = pd.DataFrame()
#             st.session_state.filtered_results = pd.DataFrame()
#             st.session_state.duplicate_values = pd.DataFrame()
#             st.session_state.column_pairs = []
#             st.session_state.thresholds = {}
#             st.success("Files reset! Please upload new files.")    

#     df1_file = st.file_uploader("Upload Master Data File", type=['xlsx', 'csv'], key="upload1")
#     df2_file = st.file_uploader("Upload New Data File", type=['xlsx', 'csv'], key="upload2")

#     if df1_file is not None and df2_file is not None:
#         if st.session_state.df1.empty and st.session_state.df2.empty:
#             st.session_state.df1 = pd.read_excel(df1_file) if df1_file.name.endswith('xlsx') else pd.read_csv(df1_file)
#             st.session_state.df2 = pd.read_excel(df2_file) if df2_file.name.endswith('xlsx') else pd.read_csv(df2_file)

#             # Ensure unique column names
#             st.session_state.df1 = ensure_unique_columns(st.session_state.df1)
#             st.session_state.df2 = ensure_unique_columns(st.session_state.df2)

#         # Proceed only if dataframes are loaded
#         if not st.session_state.df1.empty and not st.session_state.df2.empty:
#             with st.form("fuzzy_form"):
#                 st.write("Select Columns to Compare")

#                 num_pairs = st.slider("Select number of column pairs to compare", 1, 5, 1)
#                 col_pairs = []

#                 for i in range(num_pairs):
#                     st.write(f"Column Pair {i + 1}")
#                     col1 = st.selectbox(f"Select column {i + 1} from Master Data", st.session_state.df1.columns, key=f"col1_{i}")
#                     col2 = st.selectbox(f"Select column {i + 1} from New Data", st.session_state.df2.columns, key=f"col2_{i}")
#                     col_pairs.append((col1, col2))

#                 compare_button = st.form_submit_button("Compare Columns")

#                 if compare_button:
#                     all_similarity_scores = []
#                     similarity_columns = []
#                     for col1, col2 in col_pairs:
#                         similarity_scores, matched_values = fuzzy_match_columns(st.session_state.df1, st.session_state.df2, col1, col2)
#                         similarity_col = f"{col1}-{col2} Similarity %"
#                         match_col = f"Best Match in {col2}"

#                         similarity_df = st.session_state.df1.copy()
#                         similarity_df[similarity_col] = similarity_scores
#                         similarity_df[match_col] = matched_values

#                         all_similarity_scores.append(similarity_df[[similarity_col, match_col]])

#                     # Concatenate results with original data from df1
#                     st.session_state.fuzzy_results = pd.concat([st.session_state.df1] + all_similarity_scores, axis=1)
#                     st.session_state.column_pairs = col_pairs

#                     # Move the similarity columns to the front
#                     st.session_state.fuzzy_results = st.session_state.fuzzy_results[
#                         [col for pair in col_pairs for col in [f"{pair[0]}-{pair[1]} Similarity %", f"Best Match in {pair[1]}"]] +
#                         list(st.session_state.df1.columns)
#                     ]

#                     st.write("Fuzzy Matching Results")
#                     st.write(st.session_state.fuzzy_results)


# def render_fuzzy_lookup_page():   
        
#     if st.button("Reset"):
#         # Clear session state related to the uploaded files
#             initialize_session_state()
#             st.session_state.df1 = pd.DataFrame()
#             st.session_state.df2 = pd.DataFrame()
#             st.session_state.fuzzy_results = pd.DataFrame()
#             st.session_state.filtered_results = pd.DataFrame()
#             st.session_state.duplicate_values = pd.DataFrame()
#             st.session_state.column_pairs = []
#             st.session_state.thresholds = {}
#             st.success("Files reset! Please upload new files.")    
    
#     df1_file = st.file_uploader("Upload Master Data File", type=['xlsx', 'csv'], key="upload1")
#     df2_file = st.file_uploader("Upload New Data File", type=['xlsx', 'csv'], key="upload2")

    
#         # File upload


#     if df1_file is not None and df2_file is not None:
#         # Load the data only if files have been uploaded and not already loaded
#         if st.session_state.df1.empty and st.session_state.df2.empty:
#             st.session_state.df1 = pd.read_excel(df1_file) if df1_file.name.endswith('xlsx') else pd.read_csv(df1_file)
#             st.session_state.df2 = pd.read_excel(df2_file) if df2_file.name.endswith('xlsx') else pd.read_csv(df2_file)

#             # Ensure unique column names
#             st.session_state.df1 = ensure_unique_columns(st.session_state.df1)
#             st.session_state.df2 = ensure_unique_columns(st.session_state.df2)

#             # Get sheet names if they are Excel files
#             if df1_file.name.endswith('xlsx'):
#                 st.session_state.sheet_names1 = pd.ExcelFile(df1_file).sheet_names
#             else:
#                 st.session_state.sheet_names1 = ['Only one sheet in CSV']

#             if df2_file.name.endswith('xlsx'):
#                 st.session_state.sheet_names2 = pd.ExcelFile(df2_file).sheet_names
#             else:
#                 st.session_state.sheet_names2 = ['Only one sheet in CSV']

#             st.session_state.selected_sheet1 = st.selectbox("Select sheet from Master Data", st.session_state.sheet_names1)
#             st.session_state.selected_sheet2 = st.selectbox("Select sheet from New Data", st.session_state.sheet_names2)

#             st.warning("Note: The sheet selection function is currently not working. We are working on it. First sheet will select by default!")
#             # Reload data from the selected sheets if needed
#             if df1_file.name.endswith('xlsx'):
#                 st.session_state.df1 = pd.read_excel(df1_file, sheet_name=st.session_state.selected_sheet1)
#             if df2_file.name.endswith('xlsx'):
#                 st.session_state.df2 = pd.read_excel(df2_file, sheet_name=st.session_state.selected_sheet2)

#     # Proceed only if dataframes are loaded
#     if not st.session_state.df1.empty and not st.session_state.df2.empty:
#         with st.form("fuzzy_form"):
#             st.write("Select Columns to Compare")

#             # Slider to select number of column pairs (up to 5 pairs)
#             num_pairs = st.slider("Select number of column pairs to compare", 1, 5, 1)
#             col_pairs = []

#             # Allow selection of multiple column pairs based on the slider value
#             for i in range(num_pairs):
#                 st.write(f"Column Pair {i + 1}")
#                 col1 = st.selectbox(f"Select column {i + 1} from Master Data", st.session_state.df1.columns, key=f"col1_{i}")
#                 col2 = st.selectbox(f"Select column {i + 1} from New Data", st.session_state.df2.columns, key=f"col2_{i}")
#                 col_pairs.append((col1, col2))

#             compare_button = st.form_submit_button("Compare Columns")

#             if compare_button:
#                 # Perform fuzzy matching for each selected pair
#                 all_similarity_scores = []
#                 similarity_columns = []  # To store the names of the similarity columns
#                 for col1, col2 in col_pairs:
#                     similarity_scores = fuzzy_match_columns(st.session_state.df1, st.session_state.df2, col1, col2)
#                     similarity_col = f"{col1}-{col2} Similarity %"
#                     similarity_columns.append(similarity_col)
#                     similarity_df = st.session_state.df1.copy()
#                     similarity_df[similarity_col] = similarity_scores
#                     all_similarity_scores.append(similarity_df[[similarity_col]])

#                 # Concatenate results for all pairs
#                 st.session_state.fuzzy_results = pd.concat([st.session_state.df1] + all_similarity_scores, axis=1)
#                 st.session_state.column_pairs = col_pairs

#                 # Move the similarity columns to the front
#                 st.session_state.fuzzy_results = st.session_state.fuzzy_results[similarity_columns + list(st.session_state.df1.columns)]

#                 # Initialize thresholds for each column pair if not already set
#                 for col1, col2 in col_pairs:
#                     key = f"{col1}-{col2}"
#                     if key not in st.session_state.thresholds:
#                         st.session_state.thresholds[key] = 80

                

#         # Ensure 'fuzzy_results' exists and is not empty before trying to use it
#         if not st.session_state.fuzzy_results.empty:
#             # Display Fuzzy Matching Results
#             st.write("Fuzzy Matching Results")
#             st.write(st.session_state.fuzzy_results)

#             # Add sliders for filtering results for each column pair based on similarity %
#             for col1, col2 in st.session_state.column_pairs:
#                 st.subheader(f"Filter Results by Similarity % for {col1}-{col2}")
#                 similarity_col = f"{col1}-{col2} Similarity %"

#                 # Slider for each column pair
#                 threshold = st.slider(f"Set similarity threshold for {col1}-{col2}", 0, 100, st.session_state.thresholds.get(f"{col1}-{col2}", 80), key=f"threshold_{col1}_{col2}")

#                 # Update threshold in session state
#                 st.session_state.thresholds[f"{col1}-{col2}"] = threshold

          
# # Apply filtering based on all thresholds together
#             filter_condition = True
#             duplicate_condition = False  # Initialize as False to check for at least one condition

#             for col1, col2 in st.session_state.column_pairs:
#                 similarity_col = f"{col1}-{col2} Similarity %"
#                 threshold = st.session_state.thresholds[f"{col1}-{col2}"]

#                 # Filter rows where similarity is less than the threshold
#                 filter_condition &= st.session_state.fuzzy_results[similarity_col] < threshold

#                 # Update duplicate condition to be True if any condition is satisfied
#                 duplicate_condition |= st.session_state.fuzzy_results[similarity_col] >= threshold

#             # Filtered dataframe (satisfying all conditions)
#             st.session_state.filtered_results = st.session_state.fuzzy_results[filter_condition]

#             # Duplicate dataframe (where at least one similarity exceeds the thresholds)
#             st.session_state.duplicate_values = st.session_state.fuzzy_results[duplicate_condition]

#             # Display filtered results
#             st.subheader("Filtered Results (Rows meeting all thresholds)")
#             st.write(st.session_state.filtered_results)

#             # Display duplicate values
#             st.subheader("Duplicate Values (Rows exceeding at least one threshold)")
#             st.write(st.session_state.duplicate_values)


#             # Download Data as Excel File
#             def download_as_excel():
#                 """Converts two dataframes into an Excel file with two sheets."""
#                 output = BytesIO()
#                 writer = pd.ExcelWriter(output, engine='xlsxwriter')

#                 # Write each dataframe to a different sheet
#                 st.session_state.filtered_results.to_excel(writer, sheet_name='Filtered Data', index=False)
#                 st.session_state.duplicate_values.to_excel(writer, sheet_name='Duplicate Values', index=False)

#                 writer.close()  # Use close() instead of save()
#                 output.seek(0)
#                 return output

#             # Download Data as CSV File
#             def download_as_csv():
#                 """Converts two dataframes into a single CSV file with filtered and duplicate values."""
#                 filtered_csv = st.session_state.filtered_results.to_csv(index=False)
#                 duplicate_csv = st.session_state.duplicate_values.to_csv(index=False)
#                 return filtered_csv, duplicate_csv

#             # Add download buttons
#             st.download_button(
#                 label="Download as Excel",
#                 data=download_as_excel(),
#                 file_name='fuzzy_matching_results.xlsx',
#                 mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             )

#             # Download as CSV
#             filtered_csv, duplicate_csv = download_as_csv()

#             st.download_button(
#                 label="Download Filtered Data as CSV",
#                 data=filtered_csv,
#                 file_name='filtered_data.csv',
#                 mime='text/csv'
#             )

#             st.download_button(
#                 label="Download Duplicate Data as CSV",
#                 data=duplicate_csv,
#                 file_name='duplicate_data.csv',
#                 mime='text/csv'
#             )


def ensure_unique_columns(df):
    """Ensure all column names are unique."""
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df

def fuzzy_match_columns(df1, df2, col1, col2):
    """Apply fuzzy matching between two columns and return both similarity scores and matched values."""
    similarity_scores = []
    matched_values = []

    for x in df1[col1]:
        best_match = max(df2[col2], key=lambda y: fuzz.ratio(str(x), str(y)))
        similarity_score = fuzz.ratio(str(x), str(best_match))
        similarity_scores.append(similarity_score)
        matched_values.append(best_match)
    
    return similarity_scores, matched_values

def fuzzy_match_columns(df1, df2, col1, col2):
    """Apply fuzzy matching between two columns and return both similarity scores and matched values."""
    similarity_scores = []
    matched_values = []

    for x in df1[col1]:
        best_match = max(df2[col2], key=lambda y: fuzz.ratio(str(x), str(y)))
        similarity_score = fuzz.ratio(str(x), str(best_match))
        similarity_scores.append(similarity_score)
        matched_values.append(best_match)
    
    return similarity_scores, matched_values

def render_fuzzy_lookup_page():   
        
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
            st.success("Files reset! Please upload new files.")    
    
    df1_file = st.file_uploader("Upload Master Data File", type=['xlsx', 'csv'], key="upload1")
    df2_file = st.file_uploader("Upload New Data File", type=['xlsx', 'csv'], key="upload2")

    
    if df1_file is not None and df2_file is not None:
        if st.session_state.df1.empty and st.session_state.df2.empty:
            st.session_state.df1 = pd.read_excel(df1_file) if df1_file.name.endswith('xlsx') else pd.read_csv(df1_file)
            st.session_state.df2 = pd.read_excel(df2_file) if df2_file.name.endswith('xlsx') else pd.read_csv(df2_file)

            # Ensure unique column names
            st.session_state.df1 = ensure_unique_columns(st.session_state.df1)
            st.session_state.df2 = ensure_unique_columns(st.session_state.df2)

            if df1_file.name.endswith('xlsx'):
                st.session_state.sheet_names1 = pd.ExcelFile(df1_file).sheet_names
            else:
                st.session_state.sheet_names1 = ['Only one sheet in CSV']

            if df2_file.name.endswith('xlsx'):
                st.session_state.sheet_names2 = pd.ExcelFile(df2_file).sheet_names
            else:
                st.session_state.sheet_names2 = ['Only one sheet in CSV']

            st.session_state.selected_sheet1 = st.selectbox("Select sheet from Master Data", st.session_state.sheet_names1)
            st.session_state.selected_sheet2 = st.selectbox("Select sheet from New Data", st.session_state.sheet_names2)

            st.warning("Note: The sheet selection function is currently not working. We are working on it. First sheet will select by default!")
            if df1_file.name.endswith('xlsx'):
                st.session_state.df1 = pd.read_excel(df1_file, sheet_name=st.session_state.selected_sheet1)
            if df2_file.name.endswith('xlsx'):
                st.session_state.df2 = pd.read_excel(df2_file, sheet_name=st.session_state.selected_sheet2)

    if not st.session_state.df1.empty and not st.session_state.df2.empty:
        with st.form("fuzzy_form"):
            st.write("Select Columns to Compare")
            num_pairs = st.slider("Select number of column pairs to compare", 1, 5, 1)
            col_pairs = []

            for i in range(num_pairs):
                st.write(f"Column Pair {i + 1}")
                col1 = st.selectbox(f"Select column {i + 1} from Master Data", st.session_state.df1.columns, key=f"col1_{i}")
                col2 = st.selectbox(f"Select column {i + 1} from New Data", st.session_state.df2.columns, key=f"col2_{i}")
                col_pairs.append((col1, col2))

            compare_button = st.form_submit_button("Compare Columns")

            if compare_button:
                all_similarity_scores = []
                all_matched_values = []
                similarity_columns = []

                for col1, col2 in col_pairs:
                    similarity_scores, matched_values = fuzzy_match_columns(st.session_state.df1, st.session_state.df2, col1, col2)
                    similarity_col = f"{col1}-{col2} Similarity %"
                    match_col = f"Best Match in {col2}"

                    similarity_df = st.session_state.df1.copy()
                    similarity_df[similarity_col] = similarity_scores
                    similarity_df[match_col] = matched_values

                    all_similarity_scores.append(similarity_df[[similarity_col, match_col]])
                    similarity_columns.append(similarity_col)

                st.session_state.fuzzy_results = pd.concat([st.session_state.df1] + all_similarity_scores, axis=1)
                st.session_state.column_pairs = col_pairs
                st.session_state.fuzzy_results = st.session_state.fuzzy_results[similarity_columns + [f"Best Match in {col2}" for _, col2 in col_pairs] + list(st.session_state.df1.columns)]

                for col1, col2 in col_pairs:
                    key = f"{col1}-{col2}"
                    if key not in st.session_state.thresholds:
                        st.session_state.thresholds[key] = 80

        if not st.session_state.fuzzy_results.empty:
            st.write("Fuzzy Matching Results")
            st.write(st.session_state.fuzzy_results)

            for col1, col2 in st.session_state.column_pairs:
                st.subheader(f"Filter Results by Similarity % for {col1}-{col2}")
                similarity_col = f"{col1}-{col2} Similarity %"
                threshold = st.slider(f"Set similarity threshold for {col1}-{col2}", 0, 100, st.session_state.thresholds.get(f"{col1}-{col2}", 80), key=f"threshold_{col1}_{col2}")
                st.session_state.thresholds[f"{col1}-{col2}"] = threshold

            filter_condition = True
            duplicate_condition = False

            for col1, col2 in st.session_state.column_pairs:
                similarity_col = f"{col1}-{col2} Similarity %"
                threshold = st.session_state.thresholds[f"{col1}-{col2}"]
                filter_condition &= st.session_state.fuzzy_results[similarity_col] < threshold
                duplicate_condition |= st.session_state.fuzzy_results[similarity_col] >= threshold

            st.session_state.filtered_results = st.session_state.fuzzy_results[filter_condition]
            st.session_state.duplicate_values = st.session_state.fuzzy_results[duplicate_condition]

            st.subheader("Filtered Results (Rows meeting all thresholds)")
            st.write(st.session_state.filtered_results)

            st.subheader("Duplicate Values (Rows exceeding at least one threshold)")
            st.write(st.session_state.duplicate_values)

            def download_as_excel():
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                st.session_state.filtered_results.to_excel(writer, sheet_name='Filtered Data', index=False)
                st.session_state.duplicate_values.to_excel(writer, sheet_name='Duplicate Values', index=False)
                writer.close()
                output.seek(0)
                return output

            def download_as_csv():
                filtered_csv = st.session_state.filtered_results.to_csv(index=False)
                duplicate_csv = st.session_state.duplicate_values.to_csv(index=False)
                return filtered_csv, duplicate_csv

            st.download_button(
                label="Download as Excel",
                data=download_as_excel(),
                file_name='fuzzy_matching_results.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            filtered_csv, duplicate_csv = download_as_csv()

            st.download_button(
                label="Download Filtered Data as CSV",
                data=filtered_csv,
                file_name='filtered_data.csv',
                mime='text/csv'
            )

            st.download_button(
                label="Download Duplicate Data as CSV",
                data=duplicate_csv,
                file_name='duplicate_data.csv',
                mime='text/csv'
            )


if __name__ == "__main__":
    render_fuzzy_lookup_page()
