import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="SafeHer",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ SafeHer")
st.write("A personal safety website prototype.")

st.link_button(
    "Open SafeHer Website",
    "https://safeher-22e02.web.app"
)

components.iframe(
    "https://safeher-22e02.web.app",
    height=800,
    scrolling=True
)
