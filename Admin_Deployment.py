import streamlit as st

st.set_page_config(page_title="AWS Deployment", page_icon="🚀", layout="wide")

# Password protection
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Admin Access")
    password = st.text_input("Password", type="password")
    if password == "your-password-here":  # Change this!
        st.session_state.auth = True
        st.rerun()
    st.stop()

# Show deployment utility
from aws_deployment_utility_fixed import render_deployment_utility
render_deployment_utility()