"""
Issue assignment page for the survey.
"""

import streamlit as st
from survey_components import page_header
from survey_utils import save_and_navigate
from survey_data import get_random_unassigned_issue, assign_issue_to_participant


def issue_assignment_page():
    """Display the issue assignment page."""
    
    page_header(
        "Issue Assignment",
        "You will be assigned an issue to work on from your repository."
    )
    
    # Get participant info from session state
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')
    
    # Check if already assigned
    already_assigned = st.session_state['survey_responses'].get('assigned_issue', None)
    
    # Display context
    if participant_id:
        st.info(f"**Participant ID:** {participant_id}")
    if assigned_repo:
        st.info(f"**Assigned Repository:** {assigned_repo}")
    
    st.divider()
    
    # Issue assignment logic
    if already_assigned:
        # Issue already accepted and assigned in database
        issue_url = st.session_state['survey_responses'].get('issue_url')
        st.success("✅ You have accepted your issue assignment!")
        st.markdown(f"""
            <p style='font-size:18px; margin-top: 1rem;'>
            <strong>Assigned Issue:</strong> <a href="{issue_url}" target="_blank">{issue_url}</a>
            </p>
            """, unsafe_allow_html=True)
    else:
        # Get a random issue to preview (not assigned yet)
        if 'preview_issue' not in st.session_state:
            if participant_id and assigned_repo:
                with st.spinner('Finding an issue for you...'):
                    result = get_random_unassigned_issue(assigned_repo)
                
                if result['success']:
                    st.session_state['preview_issue'] = result['issue']
                else:
                    st.error(f"⚠️ {result['error']}")
                    st.warning("Please contact the study administrator if this issue persists.")
        
        # Show preview issue if available
        if 'preview_issue' in st.session_state:
            preview_issue = st.session_state['preview_issue']
            issue_url = preview_issue['url']
            
            st.markdown("""
                <p style='font-size:18px; margin-top: 1rem; margin-bottom: 1rem;'>
                <strong>Your Assigned Issue:</strong>
                </p>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <p style='font-size:18px;'>
                <a href="{issue_url}" target="_blank">{issue_url}</a>
                </p>
                """, unsafe_allow_html=True)
            
            st.info("Please review the issue above. When you're ready, click 'Accept Assignment' to confirm.")
    
    # Navigation buttons (no back button)
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    if already_assigned:
        # Standard layout for Next button
        col1, col2, col3 = st.columns([4, 1, 1])
        with col3:
            next_clicked = st.button("Next", key="issue_next")
    else:
        # Centered Accept Assignment button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            next_clicked = st.button("Accept Assignment", key="issue_accept", type="primary", use_container_width=True)
    
    if next_clicked:
        if already_assigned:
            # Already assigned, just proceed
            save_and_navigate('next')
        else:
            # Accept and assign the issue in database
            if 'preview_issue' in st.session_state:
                preview_issue = st.session_state['preview_issue']
                
                # Console debug output only (not on screen)
                print(f"DEBUG: Participant ID = {participant_id}")
                print(f"DEBUG: Issue ID = {preview_issue['id']}")
                print(f"DEBUG: Issue data = {preview_issue}")
                
                with st.spinner('Confirming your assignment...'):
                    assign_result = assign_issue_to_participant(participant_id, preview_issue['id'])
                
                print(f"DEBUG: Assignment result = {assign_result}")
                
                if assign_result['success']:
                    # Clear preview
                    if 'preview_issue' in st.session_state:
                        del st.session_state['preview_issue']

                    # Reset post-exp1 completion flag for new issue
                    st.session_state['post_exp1_completed'] = False

                    # Save to session state and proceed to next page immediately
                    # (no intermediate success message to avoid glitching)
                    save_and_navigate('next',
                                    assigned_issue=preview_issue,
                                    issue_url=preview_issue['url'],
                                    issue_id=preview_issue['id'])
                else:
                    st.error(f"⚠️ Error assigning issue: {assign_result['error']}")
                    print("Check the console/terminal for detailed error logs")
            else:
                st.error("⚠️ No issue available. Please refresh the page or contact the administrator.")
