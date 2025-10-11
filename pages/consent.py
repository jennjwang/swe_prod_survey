"""
Consent page for the developer survey.
"""

import streamlit as st
from survey_utils import next_page


def consent_page():
    """Display the consent page."""
    st.header("Developer Work Survey")
    st.markdown("""
        <p style='font-size:20px'>
        Thank you for considering participating in our study! <strong>We are researchers studying 
        software development practices and AI tool usage</strong>, and your insights are invaluable 
        to us.
        </p>
        
        <p style='font-size:20px'>
        <strong>📋 This survey consists of:</strong>
        </p>
        
        <p style='font-size:20px'>
        1. Work satisfaction and experience questions<br>
        2. AI tool usage questions<br>
        3. Self-efficacy assessment<br>
        4. Task estimation questions
        </p>
        
        <p style='font-size:20px'>
        ⌛ The survey will take approximately <strong>10–15 minutes</strong>.
        </p>
        
        <p style='font-size:20px'>
        🔒 Your responses will be kept fully anonymous and confidential.
        </p>
        """, unsafe_allow_html=True)
    
    if st.button("I am at least 18 years old and I agree to participate in this study."):
        next_page()

