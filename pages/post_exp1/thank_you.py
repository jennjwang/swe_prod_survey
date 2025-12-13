"""
Thank you page shown when participants complete all their assigned issues.
"""

import streamlit as st
from survey_components import page_header


def thank_you_page():
    """Display the final thank you page after survey completion."""
    page_header(
        "PR Implementation Complete!",
        "Thank you for implementing the PRs for your assigned issues."
    )
    


    st.success("All survey responses have been recorded successfully!")

    # # Display participant details
    # participant_id = st.session_state['survey_responses'].get('participant_id', '')
    # assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')

    # # Show summary information
    # st.markdown("---")
    # st.markdown("""
    #     <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem'>
    #     Study Summary:
    #     </p>
    #     """, unsafe_allow_html=True)

    # if participant_id:
    #     st.info(f"**Participant ID:** {participant_id}")

    # if assigned_repo:
    #     st.info(f"**Repository:** {assigned_repo}")

    # st.markdown("---")

    # Closing message
    st.markdown("""
        <div style='padding: 1rem 0;'>
            <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem;'>
            What happens next?
            </p>
            <p style='font-size:16px; margin-bottom: 1rem;'>
            Your responses have been recorded, and reviewers will begin reviewing your PRs.
            You should receive a notification once your PRs are reviewed.
            </p>
            <p style='font-size:16px; margin-bottom: 1rem;'>
            Once your PRs have been <strong>merged or closed</strong>, please return to submit your final data and complete the post-review survey.
            </p>
            <p style='font-size:16px; margin-bottom: 1rem;'>
            If you have any questions or concerns,
            please contact jennjwang@stanford.edu.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # Add button to update merged/closed PRs
    if st.button("Update Merged/Closed PR", type="primary", use_container_width=True):
        st.session_state['page'] = 18  # PR closed update page
        st.rerun()

    # Optional: View all responses (for transparency)
    # with st.expander("View your survey responses"):
    #     st.json(st.session_state['survey_responses'])

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <p style='font-size:16px; color: #666;'>
            Thank you again for your time! 🙏
            </p>
        </div>
        """, unsafe_allow_html=True)
