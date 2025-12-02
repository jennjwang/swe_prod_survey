"""
Repository assignment page for the survey.
"""

import streamlit as st
from survey_components import page_header, navigation_buttons, text_input_question
from survey_utils import save_and_navigate
from survey_data import get_repository_assignment


def repository_assignment_page():
    """Display the repository assignment page."""
    page_header(
        "Repository Assignment",
        "You will be assigned a repository to work on for this study."
    )
    
    # Get participant ID from session state (entered on first page)
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    previous_repo = st.session_state['survey_responses'].get('assigned_repository', None)
    
    # Display participant ID
    if participant_id:
        st.info(f"**Participant ID:** {participant_id}")
    
    # Show assigned repository from database
    assigned_repo = None
    repo_url = None
    
    if previous_repo:
        assigned_repo = previous_repo
        repo_url = st.session_state['survey_responses'].get('repository_url')
        st.success(f"You have been assigned repository: **{assigned_repo}**")
    else:
        if participant_id:
            result = get_repository_assignment(participant_id)
            
            if result['success']:
                assigned_repo = result['repository']
                repo_url = result['url']
                st.session_state['survey_responses']['assigned_repository'] = assigned_repo
                st.session_state['survey_responses']['repository_url'] = repo_url
                st.success(f"You have been assigned repository: **{assigned_repo}**")
            else:
                if "not found" in result['error']:
                    st.error(f"{result['error']}")
                assigned_repo = None
        else:
            st.error("Participant ID not found. Please go back and enter your email on the first page.")
    
    # Show fork instructions if repository is assigned
    forked_repo_url = None
    if assigned_repo:
        repo_url = repo_url or f"https://github.com/{assigned_repo}"
        
        st.divider()
        st.markdown("""
            <p style='font-size:20px; font-weight: 600; margin-top: 1rem; margin-bottom: 1rem'>
            Next Steps:
            </p>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <p style='font-size:18px; margin-bottom: 0.5rem'>
            1. Go to <a href="{repo_url}" target="_blank" style="color: #0066cc;">{repo_url}</a>
            </p>
            <p style='font-size:18px; margin-bottom: 0.5rem'>
            2. Create a fork of <b>the repository above</b> with your anonymous GitHub account
            </p>
            <p style='font-size:18px; margin-bottom: 1rem'>
            3. Copy and paste the URL of your forked repository below
            </p>
            """, unsafe_allow_html=True)
        
        # Load previous forked repo URL
        previous_forked_url = st.session_state['survey_responses'].get('forked_repository_url', '')
        
        forked_repo_url = text_input_question(
            "Enter your forked repository URL:",
            "forked_repo_url_input",
            previous_forked_url,
            placeholder="https://github.com/YOUR_USERNAME/repository-name"
        )
    
    # Validation function
    def validate():
        return assigned_repo and forked_repo_url
    
    def get_error_message():
        if not assigned_repo:
            return "Please wait for your repository assignment to load."
        elif not forked_repo_url:
            return "Please enter the URL of your forked repository to proceed."
        return "Please fill out all fields."
    
    # Navigation
    navigation_buttons(
        on_back=lambda: save_and_navigate('back',
                                          assigned_repository=assigned_repo,
                                          forked_repository_url=forked_repo_url),
        on_next=lambda: save_and_navigate('next',
                                          assigned_repository=assigned_repo,
                                          forked_repository_url=forked_repo_url),
        back_key="task_back",
        next_key="task_next",
        validation_fn=validate,
        validation_error=get_error_message()
    )

