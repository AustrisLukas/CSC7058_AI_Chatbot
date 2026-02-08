import streamlit as st
import pandas as pd


def render_excel():

    file = st.session_state.stored_file
    file.seek(0)
    excel_file = pd.ExcelFile(file)
    sheet_name = excel_file.sheet_names[0]
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    st.dataframe(df, use_container_width=True)
