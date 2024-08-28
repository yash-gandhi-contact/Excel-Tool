import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

def initialize_session_state():
    """Initialize session state variables if they are not already set."""
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
        st.session_state.thresholds = {}  # Store thresholds for each pair

initialize_session_state()

def fuzzy_match_columns(df1, df2, col1, col2):
    """Apply fuzzy matching between two columns."""
    similarity_scores = df1[col1].apply(lambda x: max([fuzz.ratio(str(x), str(y)) for y in df2[col2]]))
    return similarity_scores

def ensure_unique_columns(df):
    """Ensure all column names are unique."""
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df

def render_fuzzy_lookup_page():
    st.header("Fuzzy Lookup")

    # File upload
    df1_file = st.file_uploader("Upload Master Data File", type=['xlsx', 'csv'], key="upload1")
    df2_file = st.file_uploader("Upload New Data File", type=['xlsx', 'csv'], key="upload2")

    if df1_file is not None and df2_file is not None:
        # Load the data only if files have been uploaded
        if st.session_state.df1.empty and st.session_state.df2.empty:
            st.session_state.df1 = pd.read_excel(df1_file) if df1_file.name.endswith('xlsx') else pd.read_csv(df1_file)
            st.session_state.df2 = pd.read_excel(df2_file) if df2_file.name.endswith('xlsx') else pd.read_csv(df2_file)

        # Ensure unique column names
        st.session_state.df1 = ensure_unique_columns(st.session_state.df1)
        st.session_state.df2 = ensure_unique_columns(st.session_state.df2)

        with st.form("fuzzy_form"):
            st.write("Select Columns to Compare")

            # Allow selection of multiple column pairs (up to 5 pairs)
            num_pairs = st.slider("Select number of column pairs", 1, 5, 1)
            col_pairs = []
            for i in range(num_pairs):
                st.write(f"Column Pair {i + 1}")
                col1 = st.selectbox(f"Select column {i + 1} from Master Data", st.session_state.df1.columns, key=f"col1_{i}")
                col2 = st.selectbox(f"Select column {i + 1} from New Data", st.session_state.df2.columns, key=f"col2_{i}")
                col_pairs.append((col1, col2))

            compare_button = st.form_submit_button("Compare Columns")

            if compare_button:
                # Perform fuzzy matching for each pair
                all_similarity_scores = []
                for col1, col2 in col_pairs:
                    similarity_scores = fuzzy_match_columns(st.session_state.df1, st.session_state.df2, col1, col2)
                    similarity_df = st.session_state.df1.copy()
                    similarity_df[f"{col1}-{col2} Similarity %"] = similarity_scores
                    all_similarity_scores.append(similarity_df)

                # Concatenate results for all pairs and ensure unique columns
                st.session_state.fuzzy_results = pd.concat(all_similarity_scores, axis=1)
                st.session_state.fuzzy_results = ensure_unique_columns(st.session_state.fuzzy_results)
                st.session_state.column_pairs = col_pairs

                # Initialize thresholds for new pairs
                for col1, col2 in col_pairs:
                    st.session_state.thresholds[f"{col1}-{col2}"] = st.session_state.thresholds.get(f"{col1}-{col2}", 95)

    # Ensure 'fuzzy_results' exists and is not empty before trying to use it
    if "fuzzy_results" in st.session_state and not st.session_state.fuzzy_results.empty:
        # Display Fuzzy Matching Results
        st.write("Fuzzy Matching Results")
        st.write(st.session_state.fuzzy_results)

        # Slider for similarity thresholds for each column pair
        st.subheader("Set Similarity Thresholds for Each Pair")
        filtered_results_list = []
        duplicate_values_list = []

        # Create a mask for filtering rows that satisfy all thresholds
        mask = pd.Series([True] * len(st.session_state.fuzzy_results))

        for col1, col2 in st.session_state.column_pairs:
            col_name = f"{col1}-{col2} Similarity %"
            threshold = st.slider(f"Set similarity threshold for {col1}-{col2}", 0, 100, st.session_state.thresholds.get(f"{col1}-{col2}", 95), key=f"threshold_{col1}_{col2}")
            
            # Update session state with threshold value
            st.session_state.thresholds[f"{col1}-{col2}"] = threshold
            
            # Create a mask where the similarity is above the threshold
            current_mask = st.session_state.fuzzy_results[col_name] >= threshold
            mask &= current_mask  # Combine with the existing mask
            
        # Apply the combined mask to filter results
        st.session_state.filtered_results = st.session_state.fuzzy_results[mask]
        st.session_state.duplicate_values = st.session_state.fuzzy_results[~mask]

        # Display filtered results
        st.write(f"Filtered Results (Based on Similarity % thresholds)")
        st.write(st.session_state.filtered_results)

        # Duplicate Values Section
        st.subheader("Duplicate Values")
        if not st.session_state.duplicate_values.empty:
            st.write(st.session_state.duplicate_values)
        else:
            st.write("No duplicate values identified yet.")
