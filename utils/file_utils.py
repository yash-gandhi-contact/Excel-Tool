import pandas as pd
import io
import streamlit as st

def read_files(uploaded_files):
    dataframes = []
    sheet_names = []
    
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                dataframes.append(df)
                sheet_names.append("Sheet1")
            else:
                xls = pd.ExcelFile(uploaded_file)
                sheet_names.extend(xls.sheet_names)
                for sheet in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet)
                    dataframes.append(df)
        except Exception as e:
            st.error(f"Error reading file {uploaded_file.name}: {str(e)}")
            continue

    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df, sheet_names
    else:
        return pd.DataFrame(), []  # Ensure this returns a DataFrame

#def read_files(uploaded_files):
    dataframes = []
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)  # Read CSV file
            else:
                df = pd.read_excel(uploaded_file)  # Read Excel file
            dataframes.append(df)
        except Exception as e:
            st.error(f"Error reading file {uploaded_file.name}: {str(e)}")
            continue

    if dataframes:
        # Combine all DataFrames into one if multiple files were uploaded
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df  # Ensure this is a single DataFrame
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no files were read successfully



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
