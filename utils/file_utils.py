import pandas as pd
import io
import streamlit as st

def read_excel_files(uploaded_files):
    dataframes = []
    for uploaded_file in uploaded_files:
        df = pd.read_excel(uploaded_file)
        dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

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
 
