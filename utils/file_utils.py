import pandas as pd
import streamlit as st
from io import BytesIO

def download_excel(df: pd.DataFrame, filename: str):
    """
    Provides a download link for a DataFrame as an Excel file.

    Args:
        df (pd.DataFrame): The DataFrame to be downloaded.
        filename (str): The name of the file to be downloaded.
    """
    if df is not None:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Download Excel",
            data=buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def download_csv(df: pd.DataFrame, filename: str):
    """
    Provides a download link for a DataFrame as a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to be downloaded.
        filename (str): The name of the file to be downloaded.
    """
    if df is not None:
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Download CSV",
            data=buffer,
            file_name=filename,
            mime="text/csv"
        )
