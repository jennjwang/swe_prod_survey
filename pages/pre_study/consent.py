"""
Accessible Consent page for the developer survey.
"""

import streamlit as st
from survey_utils import next_page

def consent_page():
    """Display an accessible consent page."""

    # Use simple, descriptive title (for screen readers too)
    st.title("The Ripple Effects of AI in Software Development")

    # Use concise paragraphs and bullet points for readability
    st.markdown("""
    You are invited to participate in a research study about how artificial intelligence (AI) tools affect the way software developers write code. The purpose of this study is to understand how AI tools help developers work more efficiently, improve code quality, and change how responsibilities are distributed in the development process
    """)

    st.markdown("""
    #### What You Will Do
    - You will complete programming tasks that resemble real-world development work.
    - You will be assigned GitHub issues from open-source repositories (like **Flask** or **Django**).
    - You will implement fixes or new features and submit pull requests (PRs).
    - Some participants will use AI tools (such as **Cursor Pro** and **Claude Code**) with provided training; others will not.
    - You will also complete short surveys and brief interviews about your workflow and experience.
    """)

    st.markdown("""
    #### Data Collected
    While you work, your task-related computer activity will be recorded, including:
    - Screenshots of your work environment when you type or click,
    - Logs of your actions related to the task.
    
    **We will not record audio or video of you**, and **no personal information** outside the task environment will be collected.
    All recordings will be stored securely and used **only for this research**.
    """)

    st.markdown("""
    #### Study Participation
    Participation in this research is voluntary, and you may withdraw your consent at any time. Your participation will take approximately **30–40 hours** in total over the course of **6–8 weeks**, and you will receive **$30 per hour** as compensation for your time.
    """)

    st.markdown("""
    #### Privacy and Confidentiality
    The risks associated with this study are minimal. We will only collect data related to the assigned tasks and will not record any personally identifiable information. Study data will be stored securely, in compliance with Stanford University standards, minimizing the risk of confidentiality breach. Your individual privacy will be maintained during the research and in all published and written data resulting from the study. 
    """)
    st.divider()

    st.markdown("**Please save or print a copy of this page for your records.**")
    st.info("If you agree to participate, click the button below to continue.")

    # Button: full-width, descriptive label
    if st.button("I agree to participate in this study", type="primary", use_container_width=True):
        next_page()
