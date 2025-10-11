"""
Repository assignment page for the survey.
"""

import streamlit as st
from survey_components import page_header, text_input_question, navigation_buttons
from survey_utils import save_and_navigate
from survey_data import get_repository_assignment


def repository_assignment_page():
    """Display the repository assignment page."""
    page_header(
        "Repository Assignment",
        "You will be assigned a repository to work on for this study."
    )
    
    # Load previous responses
    previous_participant_id = st.session_state['survey_responses'].get('participant_id', '')
    previous_repo = st.session_state['survey_responses'].get('assigned_repository', None)
    
    # Participant ID input
    participant_id = text_input_question(
        "Please enter your Participant ID:",
        "participant_id_input",
        previous_participant_id,
        placeholder="Enter your participant ID"
    )
    
    st.divider()
    
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
                    st.error(f"⚠️ {result['error']}")
                    st.info("Note: Participant IDs are case-sensitive. Please ensure you entered it exactly as provided.")
                else:
                    st.error(result['error'])
                assigned_repo = None
        else:
            st.warning("Please enter your Participant ID to receive your repository assignment.")
    
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
            2. Click the <strong>"Fork"</strong> button in the top-right corner
            </p>
            <p style='font-size:18px; margin-bottom: 0.5rem'>
            3. Create the fork in your anonymous GitHub account
            </p>
            <p style='font-size:18px; margin-bottom: 1rem'>
            4. Copy and paste the URL of your forked repository below
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
        return participant_id and assigned_repo and forked_repo_url
    
    def get_error_message():
        if not participant_id:
            return "Please enter your Participant ID to proceed."
        elif not assigned_repo:
            return "Please wait for your repository assignment to load."
        elif not forked_repo_url:
            return "Please enter the URL of your forked repository to proceed."
        return "Please fill out all fields."
    
    # Navigation
    navigation_buttons(
        on_back=lambda: save_and_navigate('back',
                                          participant_id=participant_id,
                                          assigned_repository=assigned_repo,
                                          forked_repository_url=forked_repo_url),
        on_next=lambda: save_and_navigate('next',
                                          participant_id=participant_id,
                                          assigned_repository=assigned_repo,
                                          forked_repository_url=forked_repo_url),
        back_key="task_back",
        next_key="task_next",
        validation_fn=validate,
        validation_error=get_error_message()
    )

