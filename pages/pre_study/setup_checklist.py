"""
Setup checklist page.
Shows important setup steps after repository assignment.
"""

import streamlit as st
from survey_components import page_header


def setup_checklist_page():
    """Display setup checklist and important reminders."""
    page_header(
        "Before You Begin",
        "Please complete this checklist before starting your assigned issues."
    )

    # # Display assigned repository for context
    # assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')
    # if assigned_repo:
    #     st.info(f"**Your Assigned Repository:** {assigned_repo}")

    # st.markdown("### Setup Checklist")

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
    st.markdown("Add your Anthropic API key to set up Claude Code locally.")
    st.markdown("")
    
    # Checkbox 4
    check4 = st.checkbox("**4. Set Up SpecStory**", key="checklist_item_4")
    st.markdown("Set up SpecStory in your virtual environment following the onboarding instructions.")
    st.markdown("")
    
    # Checkbox 5
    check5 = st.checkbox("**5. Use the Screen Recording Tool**", key="checklist_item_5")
    st.markdown("We track the time you spend on each task using the recording tool. Please make sure to start the recording tool when you begin working on an issue, and stop it when you take breaks or finish for the session.")
    st.markdown("")

    # Checkbox 6
    check6 = st.checkbox("**6. AI Use Guidelines**", key="checklist_item_6")
    st.markdown("""
        You will be allowed to use AI on certain issues, but please do not include any explicit
        indicators of AI use in your code comments, commit messages, PR descriptions, and any other project documentation.
        """)
    st.markdown("")

    st.divider()

    # Check if all items are checked
    all_checked = check1 and check2 and check3 and check4 and check5 and check6

    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("Back", key="checklist_back"):
            st.session_state['page'] -= 1
            st.rerun()

    with col3:
        if st.button("Continue", key="checklist_next", type="primary", disabled=not all_checked):
            if all_checked:
                st.session_state['page'] += 1
                st.rerun()
            else:
                st.error("⚠️ Please check all items in the checklist before continuing.")
