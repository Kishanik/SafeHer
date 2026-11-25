import streamlit as st
import requests
from datetime import datetime, timezone
from urllib.parse import quote

# Must be the first Streamlit command
st.set_page_config(
    page_title="SafeHer",
    page_icon="🛡️",
    layout="wide",
)

# -------------------- PINK THEME --------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #fff0f5 0%, #fce4ec 55%, #f8bbd0 100%);
        color: #3d2430;
    }

    h1, h2, h3 {
        color: #8e3158 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f9dce7;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background-color: #c44578;
        color: white;
        border: 1px solid #c44578;
        border-radius: 12px;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-color: #8e3158;
        color: white;
        border-color: #8e3158;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.65);
        border: 1px solid #f0bfd1;
        padding: 14px;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- SETTINGS --------------------
try:
    API_KEY = st.secrets["FIREBASE_API_KEY"]
    DATABASE_URL = st.secrets["FIREBASE_DATABASE_URL"].rstrip("/")
except Exception:
    st.error(
        "Firebase settings are missing. Add FIREBASE_API_KEY and "
        "FIREBASE_DATABASE_URL in Streamlit app Secrets."
    )
    st.stop()

AUTH_URL = "https://identitytoolkit.googleapis.com/v1"
TIMEOUT = 15


# -------------------- FIREBASE HELPERS --------------------
def firebase_error(response):
    try:
        message = response.json().get("error", {}).get("message", "Unknown error")
    except Exception:
        message = "Could not read the Firebase error."

    friendly_messages = {
        "EMAIL_EXISTS": "That email already has an account. Try signing in.",
        "INVALID_EMAIL": "Enter a valid email address.",
        "INVALID_PASSWORD": "The password is incorrect.",
        "EMAIL_NOT_FOUND": "No account was found for that email.",
        "WEAK_PASSWORD": "Use a password with at least 6 characters.",
        "USER_DISABLED": "This account has been disabled.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please wait and try again.",
        "OPERATION_NOT_ALLOWED": "Enable Email/Password sign-in in Firebase Authentication.",
        "API_KEY_INVALID": "The Firebase Web API key is incorrect.",
    }

    return friendly_messages.get(message, message.replace("_", " ").title())


def firebase_auth(action, email, password):
    url = f"{AUTH_URL}/accounts:{action}?key={API_KEY}"

    response = requests.post(
        url,
        json={
            "email": email.strip(),
            "password": password,
            "returnSecureToken": True,
        },
        timeout=TIMEOUT,
    )

    if not response.ok:
        raise ValueError(firebase_error(response))

    return response.json()


def database_url(path):
    safe_path = quote(path.strip("/"), safe="/")
    return f"{DATABASE_URL}/{safe_path}.json"


def database_request(method, path, token, data=None):
    response = requests.request(
        method,
        database_url(path),
        params={"auth": token},
        json=data,
        timeout=TIMEOUT,
    )

    if not response.ok:
        raise ValueError(firebase_error(response))

    return response.json()


def get_contacts():
    data = database_request(
        "GET",
        f"users/{st.session_state.uid}/contacts",
        st.session_state.token,
    )
    return data if isinstance(data, dict) else {}


def get_sos_events():
    data = database_request(
        "GET",
        f"users/{st.session_state.uid}/sos_events",
        st.session_state.token,
    )
    return data if isinstance(data, dict) else {}


# -------------------- SESSION --------------------
if "token" not in st.session_state:
    st.session_state.token = None

if "uid" not in st.session_state:
    st.session_state.uid = None

if "email" not in st.session_state:
    st.session_state.email = None


# -------------------- HEADER --------------------
st.title("🛡️ SafeHer")
st.caption("Your personal safety companion")

st.info(
    "For immediate danger, contact local emergency services. "
    "SafeHer is not a replacement for emergency assistance."
)

# -------------------- SIGN-IN SCREEN --------------------
if not st.session_state.token:
    st.subheader("Welcome to SafeHer")
    st.write("Create an account or sign in to access your safety dashboard.")

    login_tab, register_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input("Email address", key="login_email")
            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )
            login_submit = st.form_submit_button("Sign In", use_container_width=True)

        if login_submit:
            if not login_email.strip() or not login_password:
                st.warning("Enter your email and password.")
            else:
                try:
                    user = firebase_auth(
                        "signInWithPassword",
                        login_email,
                        login_password,
                    )
                    st.session_state.token = user["idToken"]
                    st.session_state.uid = user["localId"]
                    st.session_state.email = user["email"]
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

    with register_tab:
        with st.form("register_form"):
            register_email = st.text_input("Email address", key="register_email")
            register_password = st.text_input(
                "Create password",
                type="password",
                key="register_password",
                help="Use at least 6 characters.",
            )
            register_confirm = st.text_input(
                "Confirm password",
                type="password",
                key="register_confirm",
            )
            register_submit = st.form_submit_button(
                "Create Account",
                use_container_width=True,
            )

        if register_submit:
            if not register_email.strip():
                st.warning("Enter an email address.")
            elif len(register_password) < 6:
                st.warning("Use a password with at least 6 characters.")
            elif register_password != register_confirm:
                st.warning("The passwords do not match.")
            else:
                try:
                    user = firebase_auth(
                        "signUp",
                        register_email,
                        register_password,
                    )
                    st.session_state.token = user["idToken"]
                    st.session_state.uid = user["localId"]
                    st.session_state.email = user["email"]
                    st.success("Account created.")
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

    st.stop()


# -------------------- SIGNED-IN DASHBOARD --------------------
st.sidebar.title("SafeHer")
st.sidebar.caption("Personal safety dashboard")
st.sidebar.write(f"Signed in as **{st.session_state.email}**")

if st.sidebar.button("Sign Out", use_container_width=True):
    st.session_state.token = None
    st.session_state.uid = None
    st.session_state.email = None
    st.rerun()

st.header("Your Safety Dashboard")
st.write(f"Welcome, **{st.session_state.email}**")

dashboard_tab, contacts_tab, sos_tab, account_tab = st.tabs(
    ["Dashboard", "Trusted Contacts", "SOS Alert", "Account Status"]
)

# -------------------- DASHBOARD TAB --------------------
with dashboard_tab:
    st.subheader("Safety Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Account", "Signed in")

    with col2:
        try:
            contact_count = len(get_contacts())
            st.metric("Trusted Contacts", contact_count)
        except Exception:
            st.metric("Trusted Contacts", "Unavailable")

    st.warning(
        "This prototype does not send emergency notifications. "
        "Do not rely on it as an emergency service."
    )

# -------------------- TRUSTED CONTACTS TAB --------------------
with contacts_tab:
    st.subheader("Trusted Contacts")
    st.write("Add a contact you trust. Use sample details while testing.")

    with st.form("add_contact_form", clear_on_submit=True):
        contact_name = st.text_input("Contact name")
        contact_phone = st.text_input("Phone number")
        contact_relationship = st.text_input("Relationship (optional)")
        add_contact_submit = st.form_submit_button("Add Contact")

    if add_contact_submit:
        if not contact_name.strip() or not contact_phone.strip():
            st.warning("Enter a contact name and phone number.")
        else:
            contact_data = {
                "name": contact_name.strip(),
                "phone": contact_phone.strip(),
                "relationship": contact_relationship.strip(),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            try:
                database_request(
                    "POST",
                    f"users/{st.session_state.uid}/contacts",
                    st.session_state.token,
                    contact_data,
                )
                st.success("Contact saved.")
                st.rerun()
            except Exception as error:
                st.error(f"Could not save contact: {error}")

    st.divider()
    st.subheader("Saved Contacts")

    try:
        contacts = get_contacts()

        if not contacts:
            st.info("No trusted contacts have been added yet.")
        else:
            for contact_id, contact in contacts.items():
                with st.container(border=True):
                    st.write(f"**{contact.get('name', 'Unnamed contact')}**")
                    st.write(f"Phone: {contact.get('phone', 'Not provided')}")

                    if contact.get("relationship"):
                        st.caption(contact["relationship"])

                    if st.button("Remove", key=f"remove_{contact_id}"):
                        try:
                            database_request(
                                "DELETE",
                                f"users/{st.session_state.uid}/contacts/{contact_id}",
                                st.session_state.token,
                            )
                            st.success("Contact removed.")
                            st.rerun()
                        except Exception as error:
                            st.error(f"Could not remove contact: {error}")

    except Exception as error:
        st.error(f"Could not load contacts: {error}")


# -------------------- SOS TAB --------------------
with sos_tab:
    st.subheader("SOS Alert")
    st.warning(
        "This button only records a test event in the database. "
        "It does not send a message, make a phone call, or contact emergency services."
    )

    with st.form("sos_test_form"):
        test_note = st.text_input(
            "Test note",
            value="SafeHer test event",
        )
        confirm_test = st.checkbox(
            "I understand this only saves a test record and does not notify anyone."
        )
        sos_submit = st.form_submit_button("Save Test SOS Event")

    if sos_submit:
        if not confirm_test:
            st.warning("Confirm that you understand this is only a database test.")
        else:
            event_data = {
                "note": test_note.strip() or "SafeHer test event",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "test_record_only",
            }

            try:
                database_request(
                    "POST",
                    f"users/{st.session_state.uid}/sos_events",
                    st.session_state.token,
                    event_data,
                )
                st.success("Test event saved to Firebase.")
                st.rerun()
            except Exception as error:
                st.error(f"Could not save the test event: {error}")

    st.divider()
    st.subheader("Recent Test Events")

    try:
        events = get_sos_events()

        if not events:
            st.info("No test events have been saved.")
        else:
            for event in reversed(list(events.values())):
                st.write(
                    f"**{event.get('note', 'Test event')}** — "
                    f"{event.get('created_at', 'Time unavailable')}"
                )
    except Exception as error:
        st.error(f"Could not load test events: {error}")


# -------------------- ACCOUNT TAB --------------------
with account_tab:
    st.subheader("Account Status")
    st.write(f"**Email:** {st.session_state.email}")
    st.write("**Status:** Signed in")
    st.caption("Your account is authenticated through Firebase.")
