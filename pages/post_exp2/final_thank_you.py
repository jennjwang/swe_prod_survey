"""
Final thank you page shown after completing all survey questions.
"""

import streamlit as st
from survey_components import page_header


def final_thank_you_page():
    """Display final thank you message after all survey questions are complete."""
    page_header(
        "Thank You for Completing the Study!",
        "You have successfully completed all parts of the research study."
    )

    st.success("All your responses have been recorded successfully!")

    # Closing message
    st.markdown("""
        <div style='padding: 1rem 0;'>
            <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem;'>
            What happens next?
            </p>
            <p style='font-size:16px; margin-bottom: 1rem;'>
            Your participation in this study is now complete. Thank you for your valuable contributions
            to our research on developer productivity and AI-assisted coding.
            </p>
            <p style='font-size:16px; margin-bottom: 1rem;'>
            If you have any questions or concerns,
            please contact jennjwang@stanford.edu.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <p style='font-size:16px; color: #666;'>
            Thank you again for your time and participation!
            </p>
        </div>
        """, unsafe_allow_html=True)
