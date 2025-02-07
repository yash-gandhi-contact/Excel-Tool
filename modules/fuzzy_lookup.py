import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from io import BytesIO
from datetime import datetime

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

# def fuzzy_match_columns(df1, df2, col1, col2):
#     """Apply fuzzy matching between two columns and return both similarity scores and matched values."""
#     similarity_scores = []
#     matched_values = []

#     for x in df1[col1]:
#         best_match = max(df2[col2], key=lambda y: fuzz.ratio(str(x), str(y)))
#         similarity_score = fuzz.ratio(str(x), str(best_match))
#         similarity_scores.append(similarity_score)
#         matched_values.append(best_match)
    
#     return similarity_scores, matched_values

# def fuzzy_match_columns(df1, df2, col1, col2):
#     """Apply fuzzy matching between two columns and return both similarity scores and matched values."""
#     similarity_scores = []
#     matched_values = []

#     for x in df1[col1]:
#         best_match = max(df2[col2], key=lambda y: fuzz.ratio(str(x), str(y)))
#         similarity_score = fuzz.ratio(str(x), str(best_match))
#         similarity_scores.append(similarity_score)
#         matched_values.append(best_match)
    
#     return similarity_scores, matched_values

def fuzzy_match_columns(df1, df2, col1, col2):
    """Apply fuzzy matching between two columns and return similarity scores, matched values, and original compared values."""
    similarity_scores = []
    matched_values = []
    compared_values = []

    for x in df1[col1]:
        best_match = max(df2[col2], key=lambda y: fuzz.ratio(str(x), str(y)))
        similarity_score = fuzz.ratio(str(x), str(best_match))
        similarity_scores.append(similarity_score)
        matched_values.append(best_match)
        compared_values.append(x)  # Keep the original value being compared
    
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

            st.warning("Note: The sheet selection function is currently not working. We are working on it. First sheet will select by default!" , icon="⚠️")
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
                all_original_values = []
                similarity_columns = []
                
                for col1, col2 in col_pairs:
                    similarity_scores, matched_values, original_values = fuzzy_match_columns(st.session_state.df1, st.session_state.df2, col1, col2)

                    similarity_col = f"{col1}-{col2} Similarity %"
                    match_col = f"Best Match in {col2}"
                    original_col = f"Original {col1}"  # Column for original values being compared

                    similarity_df = st.session_state.df1.copy()
                    similarity_df[similarity_col] = similarity_scores
                    similarity_df[match_col] = matched_values
                    similarity_df[original_col] = original_values

                    # Append the group of columns in the desired order
                    all_similarity_scores.append(similarity_df[[similarity_col, match_col, original_col]])

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
            # def download_as_excel():
            #     output = BytesIO()
            #     writer = pd.ExcelWriter(output, engine='xlsxwriter')
            #     st.session_state.filtered_results.to_excel(writer, sheet_name='Filtered Data', index=False)
            #     st.session_state.duplicate_values.to_excel(writer, sheet_name='Duplicate Values', index=False)
            #     writer.close()
            #     output.seek(0)
            #     return output

            # st.download_button(
            #     label="Download",
            #     data=download_as_excel(),
            #     file_name='fuzzy_matching_results.xlsx',
            #     mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            # )


if __name__ == "__main__":
    render_fuzzy_lookup_page()


