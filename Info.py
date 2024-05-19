import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DBL"
)

HtmlFile = open("hold.html", 'r', encoding='utf-8')
source_code = HtmlFile.read()
print(source_code)
components.html(source_code, height=600)

st.write("DBL so fun")

st.sidebar.success("Select an app above.")

