st.markdown("""
<style>
/* Page background */
.stApp {
    background: linear-gradient(135deg, #fff0f5 0%, #fce4ec 55%, #f8bbd0 100%);
    color: #3d2430;
}

/* Main title and section headings */
h1, h2, h3 {
    color: #8e3158 !important;
}

/* Main content area */
[data-testid="stMain"] {
    background: transparent;
}

/* Buttons */
.stButton > button {
    background-color: #c44578;
    color: white;
    border: 1px solid #c44578;
    border-radius: 12px;
    padding: 0.55rem 1.1rem;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #8e3158;
    color: white;
    border-color: #8e3158;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #fffafd;
    color: #3d2430;
    border: 1px solid #e7a3bf;
    border-radius: 10px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f9dce7;
}

/* Info and success messages */
[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)
