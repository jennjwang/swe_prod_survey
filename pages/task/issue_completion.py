"""
Issue completion check page.
Shows when participant returns after being assigned an issue.
"""

import streamlit as st
from survey_components import page_header
from survey_utils import next_page
from survey_data import mark_issue_completed


def issue_completion_page():
    """Ask participant if they have completed their assigned issue."""
    # Custom CSS for green "Yes" button
    st.markdown("""
        <style>
        /* Green button for "Yes, I've completed it" - target by data-testid */
        div[data-testid="stButton"] button[data-testid="issue_completed_yes"],
        .stButton > button[data-testid="issue_completed_yes"],
        button[data-testid="issue_completed_yes"] {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
            color: white !important;
        }
        div[data-testid="stButton"] button[data-testid="issue_completed_yes"]:hover,
        .stButton > button[data-testid="issue_completed_yes"]:hover,
        button[data-testid="issue_completed_yes"]:hover {
            background-color: #218838 !important;
            border-color: #1e7e34 !important;
            color: white !important;
        }
        div[data-testid="stButton"] button[data-testid="issue_completed_yes"]:active,
        .stButton > button[data-testid="issue_completed_yes"]:active,
        button[data-testid="issue_completed_yes"]:active {
            background-color: #1e7e34 !important;
            border-color: #1c7430 !important;
        }
        div[data-testid="stButton"] button[data-testid="issue_completed_yes"]:focus:not(:active),
        .stButton > button[data-testid="issue_completed_yes"]:focus:not(:active),
        button[data-testid="issue_completed_yes"]:focus:not(:active) {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
            box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.5) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    page_header(
        "Issue Status",
        "Let's check on your assigned issue."
    )
    
    # Get issue details from session state
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    issue_url = st.session_state['survey_responses'].get('issue_url', '')
    issue_id = st.session_state['survey_responses'].get('issue_id', '')
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')
    
    # Display issue details
    if issue_url:
        st.info(f"**Your Assigned Issue:** [{issue_url}]({issue_url})")
    
    # if assigned_repo:
    #     st.info(f"**Repository:** {assigned_repo}")
    
    st.divider()
    
    # Ask if completed
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-top: 2rem; margin-bottom: 1rem;'>
        Have you completed this issue?
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <p style='font-size:16px; margin-bottom: 1rem;'>
        Please confirm that you have:
        </p>
        <ul style='font-size:16px; margin-bottom: 1rem;'>
            <li>Implemented the required changes</li>
            <li>Tested your solution</li>
            <li>Opened a pull request with your changes</li>
        </ul>
        """, unsafe_allow_html=True)
    
    # Store completion choice in session state to show/hide PR input
    if 'completion_choice' not in st.session_state:
        st.session_state['completion_choice'] = None
    
    # Response options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "Yes, I've completed it",
            key="issue_completed_yes",
            type="primary",
            use_container_width=True
        ):
            st.session_state['completion_choice'] = 'completed'
    
    with col2:
        if st.button(
            "Not yet, still working on it",
            key="issue_completed_no",
            use_container_width=True
        ):
            st.session_state['completion_choice'] = 'not_completed'
    
    # If user selected "completed", show PR URL input
    if st.session_state.get('completion_choice') == 'completed':
        st.divider()
        st.markdown("""
            <p style='font-size:18px; font-weight:600; margin-top: 1rem; margin-bottom: 1rem;'>
            Please submit your Pull Request URL
            </p>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <p style='font-size:16px; margin-bottom: 1rem;'>
            Enter the URL of the pull request you opened for this issue:
            </p>
            """, unsafe_allow_html=True)
        
        pr_url = st.text_input(
            label="Pull Request URL",
            placeholder="https://github.com/owner/repo/pull/123",
            key="pr_url_input",
            label_visibility="collapsed"
        )
        
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        submit_button = st.button(
            "Submit Completion",
            key="submit_completion",
            type="primary",
            use_container_width=False
        )
        
        if submit_button:
            if pr_url and pr_url.strip():
                # Mark as completed in database with PR URL
                if issue_id:
                    with st.spinner('Recording your completion...'):
                        result = mark_issue_completed(issue_id, pr_url.strip())
                    
                    if result['success']:
                        print(f"✅ Issue {issue_id} marked as completed with PR: {pr_url}")
                        # Save completion status to session state
                        st.session_state['survey_responses']['issue_completed'] = True
                        st.session_state['survey_responses']['pr_url'] = pr_url.strip()
                        # Clear completion choice
                        st.session_state['completion_choice'] = None
                        
                        # Check if participant has already completed survey using progress data
                        from survey_data import get_participant_progress
                        progress_result = get_participant_progress(participant_id)
                        
                        if progress_result['success'] and progress_result['progress']['survey_completed']:
                            # Already completed survey, redirect to already completed page
                            st.session_state['page'] = 14  # Already completed page (page 14)
                        else:
                            # Route directly to post-issue questions (General Experience)
                            st.session_state['page'] = 11  # post_issue_questions_page (page 11)
                        st.rerun()
                    else:
                        st.error(f"⚠️ Error recording completion: {result['error']}")
                        print(f"Failed to mark issue as completed: {result['error']}")
                else:
                    st.error("⚠️ Issue ID not found. Please contact the study administrator.")
            else:
                st.error("⚠️ Please enter a valid pull request URL.")
    
    # If user selected "not completed", show helpful message and keep page accessible
    if st.session_state.get('completion_choice') == 'not_completed':
        st.divider()
        st.info("""
            **No problem!** Please continue working on your issue.
            
            When you complete it and open a pull request, return to this page and click "Yes, I've completed it" to submit your completion.
        """)
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        # Add a button to acknowledge and clear the message
        if st.button("Got it", key="clear_not_completed", use_container_width=False):
            st.session_state['completion_choice'] = None
            st.rerun()
        
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <p style='font-size:16px; color: #666;'>
            💡 You can refresh this page anytime to check back or submit your completion.
            </p>
            """, unsafe_allow_html=True)

