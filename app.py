import streamlit as st
import sqlite3
from twilio.rest import Client

# ---------------- TWILIO CONFIG ----------------
ACCOUNT_SID = "AC5a35ce25b21f8843caf045cc3adc1128"
AUTH_TOKEN = "6b26d38a59a63fea0668370bb4133bb5"
VERIFY_SID = "VA78f7e0ba891b7c6b59e3cdeb2763205c"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ---------------- DATABASE ----------------
conn = sqlite3.connect(r"C:\Users\PREETHI\OneDrive\Documents\hackathon_app\issue.db", check_same_thread=False)
c = conn.cursor()

# ---------------- OTP FUNCTIONS ----------------
def send_otp(phone):
    client.verify.services(VERIFY_SID).verifications.create(
        to=phone,
        channel="sms"
    )

def verify_otp(phone, otp):
    check = client.verify.services(VERIFY_SID).verification_checks.create(
        to=phone,
        code=otp
    )
    return check.status == "approved"

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "phone" not in st.session_state:
    st.session_state.phone = None

# ---------------- UI ----------------
st.set_page_config(page_title="Smart City App", layout="wide")

menu = ["Home", "Login", "Report Issue", "View Issues", "Dashboard"]
page = st.sidebar.selectbox("Navigation", menu)

# ---------------- HOME ----------------
if page == "Home":
    st.title("🌈 Smart City Citizen Portal")
    st.markdown("""
    - 📱 Mobile Friendly  
    - 🔐 OTP Secure Login  
    - 📸 Camera Support  
    - 📍 Google Maps Ready  
    - 🏛️ Citizen + Collector Dashboard  
    """)

# ---------------- LOGIN ----------------
elif page == "Login":
    st.subheader("🔐 OTP Login")

    phone = st.text_input("Phone Number (+91...)")

    if st.button("Send OTP"):
        send_otp(phone)
        st.session_state.phone = phone
        st.success("OTP sent")

    otp = st.text_input("Enter OTP")

    if st.button("Verify OTP"):
        if verify_otp(st.session_state.phone, otp):
            st.session_state.logged_in = True

            # CHECK ROLE
            c.execute("SELECT role FROM users WHERE phone=?", (phone,))
            user = c.fetchone()

            if user:
                st.session_state.role = user[0]
            else:
                st.session_state.role = "Citizen"
                c.execute("INSERT INTO users VALUES (?,?)", (phone, "Citizen"))
                conn.commit()

            st.success(f"Logged in as {st.session_state.role}")
        else:
            st.error("Invalid OTP")

# ---------------- REPORT ISSUE ----------------
elif page == "Report Issue":
    if not st.session_state.logged_in:
        st.warning("Please login first")
    else:
        st.subheader("📝 Report an Issue")

        title = st.text_input("Issue Title")
        desc = st.text_area("Description")
        location = st.text_input("Location (Google Maps link / area)")

        image = st.camera_input("Capture Image")

        if st.button("Submit Issue"):
            c.execute(
                "INSERT INTO issues (phone, title, description, location, status) VALUES (?,?,?,?,?)",
                (st.session_state.phone, title, desc, location, "Pending")
            )
            conn.commit()
            st.success("Issue reported successfully")

# ---------------- VIEW ISSUES ----------------
elif page == "View Issues":
    if not st.session_state.logged_in:
        st.warning("Please login first")
    else:
        st.subheader("📋 Reported Issues")

        if st.session_state.role == "Citizen":
            c.execute("SELECT * FROM issues WHERE phone=?", (st.session_state.phone,))
        else:
            c.execute("SELECT * FROM issues")

        issues = c.fetchall()

        for i in issues:
            st.info(f"""
            🆔 {i[0]}  
            📌 {i[2]}  
            📝 {i[3]}  
            📍 {i[4]}  
            🔄 Status: {i[5]}
            """)

# ---------------- DASHBOARD ----------------
elif page == "Dashboard":
    if not st.session_state.logged_in:
        st.warning("Please login first")
    else:
        if st.session_state.role == "Collector":
            st.subheader("🏛️ Collector Dashboard")

            c.execute("SELECT * FROM issues")
            issues = c.fetchall()

            for i in issues:
                new_status = st.selectbox(
                    f"Issue {i[0]} Status",
                    ["Pending", "In Progress", "Resolved"],
                    index=["Pending", "In Progress", "Resolved"].index(i[5])
                )

                if st.button(f"Update {i[0]}"):
                    c.execute("UPDATE issues SET status=? WHERE id=?", (new_status, i[0]))
                    conn.commit()
                    st.success("Updated")

        else:
            st.subheader("👤 Citizen Dashboard")
            st.write("Track your reported issues here.")

# ---------------- LOGOUT ----------------
if st.session_state.logged_in:
    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.phone = None
        st.success("Logged out")
