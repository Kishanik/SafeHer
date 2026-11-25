import streamlit as st
import requests
from datetime import datetime, timezone

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff0f5 0%, #fce4ec 55%, #f8bbd0 100%);
    color: #3d2430;
}

h1, h2, h3 {
    color: #8e3158 !important;
}

.stButton > button {
    background-color: #c44578;
    color: white;
    border: 1px solid #c44578;
    border-radius: 12px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #8e3158;
    color: white;
    border-color: #8e3158;
}

[data-testid="stSidebar"] {
    background-color: #f9dce7;
}
</style>
""", unsafe_allow_html=True)

# Keep the rest of your existing SafeHer code below this line.
