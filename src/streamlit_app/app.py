import streamlit as st
import pandas as pd

st.set_page_config(page_title="AutoApply App", layout="wide")

# CSS for styling
st.markdown("""
    <style>     
        h1 {
            font-size: 60px !important;
            text-align: center !important;
            color: #FF5733 !important;
        }

        p {
            font-size: 20px !important;
            text-align: left !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Home"

def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()

if st.session_state.page == "Home":
    st.markdown("<h1 style='font-size: 60px; text-align: center; color: #FF5733;'>Welcome to AutoApply App</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 24px; text-align: center;'>Your all-in-one solution for enhancing and customizing your resume to secure your dream job!</p>", unsafe_allow_html=True)

    st.write("")  

    option = st.radio("What would you like to do?", [
        "Option 1: Tailor my resume for a specific job opportunity",
        "Option 2: Find the best job matches and optimize my resume accordingly"
    ], index=None, key="paso_0")
    
    if option == "Option 1: Tailor my resume for a specific job opportunity":
        go_to_page("Option1")

    if option == "Option 2: Find the best job matches and optimize my resume accordingly":
        go_to_page("Option2")

# Load pages dynamically
elif st.session_state.page == "Option1":
    import option1
    option1.run()

elif st.session_state.page == "Option1_1":
    import option1_1
    option1_1.run()

elif st.session_state.page == "Option1_2":
    import option1_2
    option1_2.run()

elif st.session_state.page == "Option1_3":
    import option1_3
    option1_3.run()

elif st.session_state.page == "Option1_4":
    import option1_4
    option1_4.run()


elif st.session_state.page == "Option2":
    import option2
    option2.run()
