
import streamlit as st
import requests
from datetime import datetime, timezone
from urllib.parse import quote

st.set_page_config(
    page_title="SafeHer | Women Safety",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #fff8fb;
}
h1, h2, h3 {
    color: #8b315d;
}
div.stButton > button {
    background-color: #8b315d;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets["FIREBASE_API_KEY"]
DATABASE_URL = st.secrets["FIREBASE_DATABASE_URL"].rstrip("/")

AUTH_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts"
)

def firebase_auth(endpoint, email, password):
    url = f"{AUTH_URL}:{endpoint}?key={API_KEY}"

    response = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        },
        timeout=20
    )

    data = response.json()

    if response.status_code != 200:
        error = data.get("error", {}).get("message", "Login failed")
        raise ValueError(error)

    return data


def database_request(method, path, data=None):
    token = st.session_state.get("id_token")

    url = (
        f"{DATABASE_URL}/{path}.json"
        f"?auth={quote(token)}"
    )

    response = requests.request(
        method,
        url,
        json=data,
        timeout=20
    )

    if response.status_code >= 400:
        raise ValueError("Firebase database request failed.")

    return response.json()


def login_user(email, password):
    data = firebase_auth(
        "signInWithPassword",
        email,
        password
    )

    st.session_state["id_token"] = data["idToken"]
    st.session_state["uid"] = data["localId"]
    st.session_state["email"] = data["email"]


def register_user(email, password):
    data = firebase_auth(
        "signUp",
        email,
        password
    )

    st.session_state["id_token"] = data["idToken"]
    st.session_state["uid"] = data["localId"]
    st.session_state["email"] = data["email"]


def logout():
    for key in ["id_token", "uid", "email"]:
        st.session_state.pop(key, None)

    st.rerun()


def user_path():
    return f"users/{st.session_state['uid']}"


def show_login():
    st.title("🛡️ SafeHer")
    st.subheader("Your personal safety companion")

    st.write(
        "Create an account or sign in to access your "
        "personal safety dashboard."
    )

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if submitted:
            try:
                login_user(email.strip(), password)
                st.success("Login successful!")
                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except requests.RequestException:
                st.error("Unable to connect to Firebase.")

    with register_tab:
        with st.form("register_form"):
            email = st.text_input(
                "Email address",
                key="register_email"
            )

            password = st.text_input(
                "Create password",
                type="password",
                key="register_password"
            )

            confirm = st.text_input(
                "Confirm password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if submitted:
            if password != confirm:
                st.error("Passwords do not match.")

            elif len(password) < 6:
                st.error("Password must contain at least 6 characters.")

            else:
                try:
                    register_user(email.strip(), password)
                    st.success("Account created successfully!")
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

                except requests.RequestException:
                    st.error("Unable to connect to Firebase.")


def show_dashboard():
    uid = st.session_state["uid"]
    email = st.session_state["email"]

    st.title("🛡️ SafeHer Dashboard")

    st.write(f"Welcome, {email}")

    if st.button("Logout"):
        logout()

    st.divider()

    st.warning(
        "For immediate danger, contact local emergency "
        "services. SafeHer is not a replacement for "
        "emergency assistance."
    )

    home_tab, contacts_tab, sos_tab = st.tabs(
        ["Dashboard", "Trusted Contacts", "SOS Alert"]
    )

    with home_tab:
        st.subheader("Your Safety Dashboard")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Account Status", "Active")

        with col2:
            st.metric("Safety App", "Ready")

        st.info(
            "Add trusted contacts and keep their details "
            "updated before using the SOS feature."
        )

    with contacts_tab:
        st.subheader("Trusted Contacts")

        with st.form("contact_form"):
            contact_name = st.text_input("Contact name")
            contact_phone = st.text_input("Phone number")

            submitted = st.form_submit_button(
                "Save Contact"
            )

        if submitted:
            if not contact_name or not contact_phone:
                st.error("Enter both contact name and phone number.")

            else:
                try:
                    database_request(
                        "POST",
                        f"{user_path()}/contacts",
                        {
                            "name": contact_name,
                            "phone": contact_phone,
                            "created_at": datetime.now(
                                timezone.utc
                            ).isoformat()
                        }
                    )

                    st.success("Contact saved successfully!")
                    st.rerun()

                except Exception as error:
                    st.error(f"Could not save contact: {error}")

        try:
            contacts = database_request(
                "GET",
                f"{user_path()}/contacts"
            ) or {}

            if contacts:
                for contact_id, contact in contacts.items():
                    st.write(
                        f"**{contact.get('name', 'Contact')}**"
                    )
                    st.write(contact.get("phone", ""))
                    st.divider()
            else:
                st.info("No trusted contacts saved yet.")

        except Exception:
            st.error("Unable to load trusted contacts.")

    with sos_tab:
        st.subheader("Emergency SOS Alert")

        st.write(
            "Use this form to record an emergency alert "
            "in your SafeHer account."
        )

        with st.form("sos_form"):
            location = st.text_input(
                "Your current location",
                placeholder="Enter your location"
            )

            message = st.text_area(
                "Emergency message",
                value="I need help. Please contact me."
            )

            submitted = st.form_submit_button(
                "Record SOS Alert",
                use_container_width=True
            )

        if submitted:
            try:
                database_request(
                    "POST",
                    f"{user_path()}/alerts",
                    {
                        "location": location,
                        "message": message,
                        "status": "recorded",
                        "created_at": datetime.now(
                            timezone.utc
                        ).isoformat()
                    }
                )

                st.success(
                    "SOS alert recorded in your Firebase account."
                )

                st.info(
                    "This does not automatically send SMS, "
                    "make phone calls, or notify your contacts."
                )

            except Exception as error:
                st.error(f"Could not record alert: {error}")


if "id_token" not in st.session_state:
    show_login()
else:
    show_dashboard()
