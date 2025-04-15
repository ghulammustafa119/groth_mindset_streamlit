
import streamlit as st
import pandas as pd
import os
from io import BytesIO

# set up our app
st.set_page_config(page_title="Data Sweeper", layout='wide')
st.title("Data Sweeper by Ghulam Mustafa Bhutto")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        file_size_kb = len(file.getvalue()) / 1024
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file_size_kb:.2f} KB")

        st.write("Preview the Head of the Dataframe")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}", key=f"remove_dup_{file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")
                    st.dataframe(df.head())

            with col2:
                if st.button(f"Fill Missing Values for {file.name}", key=f"fill_na_{file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values Filled!")
                    st.dataframe(df.head())

        # Choose Specific Columns to Keep or Convert
        st.subheader("Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Create Some Visualizations
        st.subheader("Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            num_cols = df.select_dtypes(include='number')
            if not num_cols.empty and num_cols.shape[1] > 1:
                st.bar_chart(num_cols.iloc[:, :2])
            else:
                st.warning("Not enough numeric data for visualization!")

        # Convert the File -> CSV to Excel
        st.subheader("Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"convert_{file.name}")
        
        if st.button(f"Convert {file.name}", key=f"convert_btn_{file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            buffer.seek(0)

            # Download Button
            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("All files processed!")