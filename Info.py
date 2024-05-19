HtmlFile = open("hold.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()
print(source_code)
components.html(source_code, height=600)

import streamlit as st

st.set_page_config(
    page_title="DBL"
)

st.write("DBL so fun")

st.sidebar.success("Select an app above.")

