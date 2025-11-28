"""
Issue completion check page.
Shows when participant returns after being assigned an issue.
"""

import streamlit as st
import re
from survey_components import page_header
from survey_data import mark_issue_completed, get_participant_progress


def is_valid_pr_url(url):
    """Validate that the URL is a GitHub pull request URL."""
    if not url or not url.strip():
        return False

    # Pattern for GitHub PR URLs: https://github.com/owner/repo/pull/number
    pattern = r'^https?://github\.com/[\w-]+/[\w.-]+/pull/\d+/?$'
    return bool(re.match(pattern, url.strip()))


def issue_completion_page():
    """Ask participant if they have completed their assigned issue."""
    page_header("Issue Status", "Let's check on your assigned issue.")

    # Get issue details from session state
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    issue_url = st.session_state['survey_responses'].get('issue_url', '')
    issue_id = st.session_state['survey_responses'].get('issue_id', '')
    using_ai = st.session_state['survey_responses'].get('current_issue_using_ai', False)

    # Display issue details
    if issue_url:
        st.info(f"**Your Assigned Issue:** [{issue_url}]({issue_url})")

    # Display AI condition
    if using_ai:
        st.warning("**AI Condition:** You MAY use AI tools for this issue.")
    else:
        st.warning("**AI Condition:** You should NOT use AI tools for this issue.")

    st.divider()

    # Ask if completed
    st.subheader("Have you completed this issue?")
    st.markdown("""
        Please confirm that you have:
        - Implemented the required changes
        - Tested your solution
        - Opened a pull request to the swe-productivity fork with your changes
        """)
    
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
    
    # If user selected "completed", show PR URL input and optional file uploads
    if st.session_state.get('completion_choice') == 'completed':
        st.divider()
        st.subheader("Please submit your Pull Request URL")
        st.write("Create a pull request to the swe-productivity fork with your changes:")
        
        pr_url = st.text_input(
            label="Pull Request URL",
            placeholder="https://github.com/owner/repo/pull/123",
            key="pr_url_input",
            label_visibility="collapsed"
        )

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        st.subheader("Upload Required Data")
        st.write("Please review your data to exclude any sensitive information before submitting.")

        st.markdown("**1. SpecStory Folder**")
        st.caption("Upload a zipped copy of your `.specstory` folder from the assigned repository.")
        specstory_upload = st.file_uploader(
            "Upload .specstory folder (zipped)",
            type=['zip'],
            key="specstory_upload",
            label_visibility="collapsed"
        )

        st.markdown("")
        st.markdown("**2. Screen Recorder Data**")
        st.caption("Upload a zipped copy of the `/data` folder from your screen recorder directory.")
        screenrec_upload = st.file_uploader(
            "Upload screen recorder /data folder (zipped)",
            type=['zip'],
            key="screenrec_upload",
            label_visibility="collapsed"
        )

        submit_button = st.button(
            "Submit Completion",
            key="submit_completion",
            type="primary"
        )

        # st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
        
        if submit_button:
            # Basic validations
            if not pr_url or not pr_url.strip():
                st.error("⚠️ Please enter a pull request URL.")
                return
            # if not is_valid_pr_url(pr_url):
            #     st.error("⚠️ Please enter a valid GitHub pull request URL (e.g., https://github.com/owner/repo/pull/123)")
            #     return
            if not issue_id:
                st.error("⚠️ Issue ID not found. Please contact the study administrator.")
                return
            # Enforce both uploads present
            if not specstory_upload or not screenrec_upload:
                st.error("⚠️ Please upload both the SpecStory zip and the screen recorder data zip before submitting.")
                return

            # Upload files to Drive as part of submission
            try:
                from .drive_upload import upload_to_drive_in_subfolders, sanitize_filename
                folder_id = st.secrets.get('GDRIVE_FOLDER_ID', '')
                if not folder_id:
                    st.error("Drive folder not configured. Ask the admin to set GDRIVE_FOLDER_ID in secrets.")
                    return
                with st.spinner('Uploading your files...'):
                    participant_folder = sanitize_filename(participant_id) if participant_id else "unknown_participant"
                    issue_folder = f"issue_{issue_id}"
                    subfolders = [participant_folder, issue_folder]
                    # Upload SpecStory zip
                    upload_to_drive_in_subfolders(
                        specstory_upload,
                        folder_id,
                        subfolders=subfolders,
                        filename=specstory_upload.name,
                    )
                    # Upload screen recorder zip
                    upload_to_drive_in_subfolders(
                        screenrec_upload,
                        folder_id,
                        subfolders=subfolders,
                        filename=screenrec_upload.name,
                    )
            except Exception as e:
                st.error(f"Upload failed: {e}")
                return

            # Mark as completed in database with PR URL
            with st.spinner('Recording your completion...'):
                result = mark_issue_completed(issue_id, pr_url.strip())

            if result['success']:
                print(f"✅ Issue {issue_id} marked as completed with PR: {pr_url}")

                # Save completion status to session state
                st.session_state['survey_responses']['issue_completed'] = True
                st.session_state['survey_responses']['pr_url'] = pr_url.strip()
                st.session_state['completion_choice'] = None

                # Check if survey already completed
                progress_result = get_participant_progress(participant_id)

                if progress_result['success'] and progress_result['progress']['survey_completed']:
                    # Survey already complete, go to completion page
                    st.session_state['page'] = 16
                else:
                    # Go to AI condition questions (will auto-skip if not using AI)
                    st.session_state['page'] = 11

                st.rerun()
            else:
                st.error(f"⚠️ Error recording completion: {result['error']}")
                print(f"Failed to mark issue as completed: {result['error']}")
    
    # If user selected "not completed", show helpful message
    if st.session_state.get('completion_choice') == 'not_completed':
        st.divider()
        st.info("""
            No problem! Please continue working on your issue.

            When you complete it and open a pull request, return to this page to submit your completion.
        """)

        st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)

        # if st.button("Got it", key="clear_not_completed"):
        #     st.session_state['completion_choice'] = None
        #     st.rerun()

        # st.caption("💡 You can refresh this page anytime to check back or submit your completion.")
