import pandas as pd
import io
import streamlit as st

def read_files(uploaded_files):
    dataframes = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.name.split('.')[-1].lower()
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_type}")
            continue
        dataframes.append(df)
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no valid files were processed

def download_excel(df, file_name):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Updated Data')
    buffer.seek(0)
    st.download_button(
        label="Download Updated Excel",
        data=buffer,
        file_name=file_name,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
