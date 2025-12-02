"""
Setup checklist page.
Shows important setup steps after repository assignment.
"""

import streamlit as st
from survey_components import page_header
from survey_data import get_participant_progress, mark_checklist_completed


def setup_checklist_page():
    """Display setup checklist and important reminders."""
    # Check participant progress so we can skip if the checklist is already completed
    participant_id = st.session_state['survey_responses'].get('participant_id')
    if participant_id:
        progress_result = get_participant_progress(participant_id)
        if progress_result.get('success') and progress_result.get('progress'):
            progress_data = progress_result['progress']
            # If checklist is already completed, skip the page
            if progress_data.get('checklist_completed'):
                st.session_state['page'] += 1
                st.rerun()
                return

    page_header(
        "Before You Begin",
        "Please complete this checklist before starting your assigned issues."
    )

    # Display assigned repository for context
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')
    repo_url = st.session_state['survey_responses'].get('repository_url', '')

    if assigned_repo and repo_url:
        st.info(f"**Your Assigned Repository:** [{assigned_repo}]({repo_url})")
    elif assigned_repo:
        st.info(f"**Your Assigned Repository:** {assigned_repo}")

    # Checkbox 1
    check1 = st.checkbox("**1. Read the Contributor Guide**", key="checklist_item_1")
    st.markdown("Before you begin, please read the project's contributor guide in full.")
    st.markdown("")

    # Checkbox 2
    check2 = st.checkbox("**2. Set Up the Project**", key="checklist_item_2")
    st.markdown("Follow the setup steps in the repository to install all required tools and dependencies.")
    st.markdown("")

    # Checkbox 3
    check3 = st.checkbox("**3. Set Up Claude Code**", key="checklist_item_3")
    st.markdown("Add your Anthropic API key to .env file to set up Claude Code locally.")
    st.markdown("")
    
    # Checkbox 4
    check4 = st.checkbox("**4. Set Up SpecStory**", key="checklist_item_4")
    st.markdown("""Set up SpecStory in your virtual environment following the onboarding instructions. 
    The SpecStory extension should come pre-installed from onboarding, but you will need to install the CLI to your virtual environment.""")
    st.markdown("""
    ```bash
    bash install_specstory_wrapper.sh
    ```
    """)
    st.markdown("")
    
    # Checkbox 5
    check5 = st.checkbox("**5. Use the Screen Recording Tool**", key="checklist_item_5")
    st.markdown("We track the time you spend on each task using the recording tool. Please make sure to start the recording tool when you begin working on an issue, and stop it when you take breaks or finish for the session.")
    st.markdown("")

    # Checkbox 6
    check6 = st.checkbox("**6. AI Use Guidelines**", key="checklist_item_6")
    st.markdown("""
       You will be asked to use AI on specific issues, but please avoid explicit AI references. We provide git hooks to automatically check for AI indicators. 
       Run the following command to set up the git hooks:
        """)
    st.markdown("""
    ```bash
    pip install pre-commit
    pre-commit install
    ```
    """)
    st.markdown("")

    st.divider()

    st.markdown("""
    <p style='font-size:16px; margin-bottom: 1rem;'>
    If you run into any issues during setup, please contact jennjwang@stanford.edu.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("")

    # Check if all items are checked
    all_checked = check1 and check2 and check3 and check4 and check5 and check6

    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])

    with col3:
        if st.button("Continue", key="checklist_next", type="primary", disabled=not all_checked):
            if all_checked:
                participant_id = st.session_state['survey_responses'].get('participant_id')
                if not participant_id:
                    st.error("⚠️ Participant ID missing. Please go back and enter your email before continuing.")
                    return

                st.session_state['survey_responses']['checklist_completed'] = True
                result = mark_checklist_completed(participant_id)
                if not result['success']:
                    st.error(f"⚠️ There was an error saving your checklist completion: {result['error']}")
                    st.warning("Please contact the study administrator for assistance.")
                    return

                st.session_state['page'] += 1
                st.rerun()
            else:
                st.error("⚠️ Please check all items in the checklist before continuing.")
