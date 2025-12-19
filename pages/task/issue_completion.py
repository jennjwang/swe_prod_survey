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
    # Get issue details from session state
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    issue_url = st.session_state['survey_responses'].get('issue_url', '')
    issue_id = st.session_state['survey_responses'].get('issue_id', '')
    using_ai = st.session_state['survey_responses'].get('current_issue_using_ai', False)

    # Track assigned/completed counts to handle repos with fewer available issues
    assigned_count = 0
    completed_count = 0
    if participant_id:
        from survey_data import supabase_client
        try:
            counts_result = supabase_client.table('repo-issues')\
                .select('is_completed', count='exact')\
                .eq('participant_id', participant_id)\
                .execute()
            assigned_count = counts_result.count if counts_result.count is not None else (len(counts_result.data) if counts_result.data else 0)
            completed_count = sum(1 for issue in (counts_result.data or []) if issue.get('is_completed'))
        except Exception as e:
            print(f"Error getting issue counts: {e}")

    # Only show current issue section if there's an active issue assigned
    if issue_url and issue_id:
        print(f"DEBUG: issue_url: {issue_url}, issue_id: {issue_id}, using_ai: {using_ai}")
        page_header("Issue Status", "Let's check on your currently assigned issue.")

        # Display issue details
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
            st.info("**Large files (>1GB):** If your recording is too large, please use [this Google Form](https://forms.gle/92Juk68xzjkC7vxg8) instead.")
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
                    st.error("Issue ID not found. Please contact the study administrator.")
                    return
                # Upload files to Drive if provided
                try:
                    from .drive_upload import upload_to_drive_in_subfolders, sanitize_filename
                    folder_id = st.secrets.get('GDRIVE_FOLDER_ID', '')
                    if folder_id and (specstory_upload or screenrec_upload):
                        with st.spinner('Uploading your files...'):
                            participant_folder = sanitize_filename(participant_id) if participant_id else "unknown_participant"
                            issue_folder = f"issue_{issue_id}"
                            subfolders = [participant_folder, issue_folder]
                            # Upload SpecStory zip if provided
                            if specstory_upload:
                                upload_to_drive_in_subfolders(
                                    specstory_upload,
                                    folder_id,
                                    subfolders=subfolders,
                                    filename=specstory_upload.name,
                                )
                            # Upload screen recorder zip if provided
                            if screenrec_upload:
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
                    print(f"Issue {issue_id} marked as completed with PR: {pr_url}")

                    # Save completion status to session state
                    st.session_state['survey_responses']['issue_completed'] = True
                    st.session_state['survey_responses']['pr_url'] = pr_url.strip()
                    st.session_state['completion_choice'] = None

                    # Check if survey already completed
                    progress_result = get_participant_progress(participant_id)

                    if progress_result['success'] and progress_result['progress']['issue_survey_completed']:
                        # Survey already complete, go to completion page
                        st.session_state['page'] = 16
                    else:
                        # Go to AI condition questions (will auto-skip if not using AI)
                        st.session_state['page'] = 11

                    st.rerun()
                else:
                    st.error(f"Error recording completion: {result['error']}")
                    print(f"Failed to mark issue as completed: {result['error']}")

        # If user selected "not completed", show helpful message
        if st.session_state.get('completion_choice') == 'not_completed':
            # st.divider()
            st.markdown("""
                <div style='margin-top: 2rem;'>
                </div>
                """, unsafe_allow_html=True)
            st.info("""
                No problem! Please continue working on your issue. When you complete it and open a pull request, return to this page to submit your completion.
            """)

            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

            # if st.button("Got it", key="clear_not_completed"):
            #     st.session_state['completion_choice'] = None
            #     st.rerun()

            # st.caption("💡 You can refresh this page anytime to check back or submit your completion.")

    else:
        # No active issue assigned - show message
        page_header("Issue Status", "Check your issue status and manage completed PRs.")

        st.info(
        f"You have completed {completed_count} of {assigned_count} assigned issues."
        )

    st.divider()

    st.subheader("Check on previous PRs")

    if issue_id and issue_url:
        st.info(
        f"You have completed {completed_count} of {assigned_count} assigned issues."
        )

    st.markdown("Once you have completed a PR, you can enter its URL to check its AI condition:")

    check_issue_url = st.text_input(
        label="PR URL to check",
        placeholder="https://github.com/owner/repo/pull/123",
        key="check_issue_url",
        label_visibility="collapsed"
    )

    if st.button("Check conditions", key="check_issue_button"):
        if not check_issue_url or not check_issue_url.strip():
            st.error("Please enter a PR URL.")
        else:
            # Query database for this issue URL
            from survey_data import supabase_client

            with st.spinner('Checking PR...'):
                result = supabase_client.table('repo-issues')\
                    .select('using_ai, issue_url, pr_url, issue_id')\
                    .eq('pr_url', check_issue_url.strip())\
                    .execute()

                if result.data and len(result.data) > 0:
                    issue_data = result.data[0]
                    using_ai = issue_data.get('using_ai')
                    issue_url = issue_data.get('issue_url')
                    pr_url = issue_data.get('pr_url')
                    
                    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                    # st.success(f"PR found: {check_issue_url}")
                    if issue_url:
                        # Extract the last digit from the issue URL
                        last_digit = pr_url.rstrip('/').split('/')[-1]
                        st.info(f"**Associated Issue:** {issue_url}")
                    if using_ai is True:
                        st.warning("**AI Condition:** You MAY use AI tools for this issue.")
                    elif using_ai is False:
                        st.warning("**AI Condition:** You should NOT use AI tools for this issue.")
                    st.write("Please use this command for recording data during code review:")
                    st.code(f"swe-prod-recorder --pr {last_digit}", language="bash")

                else:
                    st.error(f"PR URL not found in the database. Please check the URL and try again.")

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.divider()

    st.subheader("Update a merged/closed PR")
    st.markdown("""
    If you have discussed your pull request with reviewers and it has been **merged or closed**,
    you can update the status of a previous PR here and submit your screen recorder data.
    """)
    if st.button("Update PR"):
        st.session_state['page'] = 18  # PR closed update page
        st.rerun()
