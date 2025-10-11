"""
Pre-study completion page.
"""

import streamlit as st
from survey_data import save_survey_responses


def pre_study_complete_page():
    """Display the pre-study survey completion page."""
    st.header("Pre-Study Survey Complete")
    
    st.markdown("""
        <p style='font-size:20px; margin-top: 2rem;'>
        Thank you for completing the pre-study survey! 
        </p>
        <p style='font-size:20px;'>
        Your answers are now recorded.
        </p>
        """, unsafe_allow_html=True)
    
    # Save responses to database (only once)
    if 'pre_study_saved' not in st.session_state:
        participant_id = st.session_state['survey_responses'].get('participant_id', '')
        
        if participant_id:
            with st.spinner('Saving your responses...'):
                result = save_survey_responses(participant_id, st.session_state['survey_responses'])
            
            if result['success']:
                st.success("✅ Your responses have been saved successfully.")
                st.session_state['pre_study_saved'] = True
            else:
                st.error(f"⚠️ There was an error saving your responses: {result['error']}")
                st.warning("Please contact the study administrator.")
        else:
            st.warning("⚠️ No participant ID found. Responses were not saved to database.")
    else:
        st.success("✅ Your responses have been saved successfully.")
    
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    
    # Continue button
    if st.button("Continue to Issue Assignment", key="continue_to_issue", type="primary"):
        from survey_utils import next_page
        next_page()

