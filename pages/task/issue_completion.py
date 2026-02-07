"""
Issue completion check page.
Shows when participant returns after being assigned an issue.
"""

import streamlit as st
import re
from survey_components import page_header
from survey_data import (
    mark_issue_completed,
    check_pr_survey_completion,
    get_missing_post_pr_surveys,
)


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

            # File size limit (MB) – must match .streamlit/config.toml maxUploadSize
            max_file_size_mb = 500
            max_file_size_bytes = max_file_size_mb * 1024 * 1024

            st.markdown("**1. SpecStory Folder**")
            st.caption("Upload a zipped copy of your `.specstory` folder from the assigned repository. **Maximum %d MB per file.**" % max_file_size_mb)
            specstory_upload = st.file_uploader(
                "Upload .specstory folder (zipped)",
                type=['zip'],
                key="specstory_upload",
                label_visibility="collapsed"
            )
            if specstory_upload and specstory_upload.size is not None:
                st.caption(f"Selected: {specstory_upload.name} — {specstory_upload.size / (1024*1024):.1f} MB")

            st.markdown("")
            st.markdown("**2. Screen Recorder Data**")
            st.caption("Upload a zipped copy of the `/data` folder from your screen recorder directory. **Maximum %d MB per file.**" % max_file_size_mb)
            st.warning("**Large files (>500MB):** If your recording is too large, please use [this Google Form](https://forms.gle/92Juk68xzjkC7vxg8) instead.")
            screenrec_upload = st.file_uploader(
                "Upload screen recorder /data folder (zipped)",
                type=['zip'],
                key="screenrec_upload",
                label_visibility="collapsed"
            )
            if screenrec_upload and screenrec_upload.size is not None:
                st.caption(f"Selected: {screenrec_upload.name} — {screenrec_upload.size / (1024*1024):.1f} MB")

            # Block submit when any file is over the limit (or size unknown)
            def _over_limit(upload):
                return upload and (upload.size is None or upload.size > max_file_size_bytes)
            specstory_over = _over_limit(specstory_upload)
            screenrec_over = _over_limit(screenrec_upload)
            if specstory_over:
                size_mb = f"{specstory_upload.size / (1024*1024):.0f} MB" if specstory_upload.size is not None else "unknown size"
                st.error(f"⚠️ SpecStory file is too large ({size_mb}). Please keep uploads under {max_file_size_mb} MB or use the Google Form for larger files.")
            if screenrec_over:
                size_mb = f"{screenrec_upload.size / (1024*1024):.0f} MB" if screenrec_upload.size is not None else "unknown size"
                st.error(f"⚠️ Screen recorder file is too large ({size_mb}). Please keep uploads under {max_file_size_mb} MB or use the Google Form for larger files.")
            any_over = specstory_over or screenrec_over

            submit_button = False
            if not any_over:
                submit_button = st.button(
                    "Submit Completion",
                    key="submit_completion",
                    type="primary",
                )

            if submit_button:
                # Basic validations
                if not pr_url or not pr_url.strip():
                    st.error("⚠️ Please enter a pull request URL.")
                    return
                if not issue_id:
                    st.error("Issue ID not found. Please contact the study administrator.")
                    return
                # Re-validate file size at submit time (must block here; UI state can be stale)
                if specstory_upload and (specstory_upload.size is None or specstory_upload.size > max_file_size_bytes):
                    st.error(f"⚠️ SpecStory file is too large or could not be checked. Please keep uploads under {max_file_size_mb} MB or use the Google Form for larger files.")
                    return
                if screenrec_upload and (screenrec_upload.size is None or screenrec_upload.size > max_file_size_bytes):
                    st.error(f"⚠️ Screen recorder file is too large or could not be checked. Please keep uploads under {max_file_size_mb} MB or use the Google Form for larger files.")
                    return
                # Upload files to Drive only if both pass size check (no submission of large files)
                def _ok_to_upload(upload):
                    return upload and upload.size is not None and upload.size <= max_file_size_bytes
                if not _ok_to_upload(specstory_upload) and specstory_upload:
                    st.error(f"⚠️ SpecStory file is too large. Submission not allowed. Please keep uploads under {max_file_size_mb} MB or use the Google Form.")
                    return
                if not _ok_to_upload(screenrec_upload) and screenrec_upload:
                    st.error(f"⚠️ Screen recorder file is too large. Submission not allowed. Please keep uploads under {max_file_size_mb} MB or use the Google Form.")
                    return
                try:
                    from .drive_upload import upload_to_drive_in_subfolders, sanitize_filename
                    folder_id = st.secrets.get('GDRIVE_FOLDER_ID', '')
                    if folder_id and (specstory_upload or screenrec_upload):
                        with st.spinner('Uploading your files...'):
                            participant_folder = sanitize_filename(participant_id) if participant_id else "unknown_participant"
                            issue_folder = f"issue_{issue_id}"
                            subfolders = [participant_folder, issue_folder]
                            if specstory_upload and _ok_to_upload(specstory_upload):
                                upload_to_drive_in_subfolders(
                                    specstory_upload,
                                    folder_id,
                                    subfolders=subfolders,
                                    filename=specstory_upload.name,
                                )
                            if screenrec_upload and _ok_to_upload(screenrec_upload):
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

                    # Check if the current issue's post-PR survey is already completed
                    survey_check = check_pr_survey_completion(participant_id, int(issue_id))

                    if survey_check.get('success') and survey_check.get('completed'):
                        # Survey already complete for this issue, go to completion page
                        st.session_state['page'] = 16
                    else:
                        # Go to post-issue questions (AI reflection handled there)
                        st.session_state['page'] = 12

                    from survey_utils import clear_form_cache_between_issues
                    clear_form_cache_between_issues()
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

    # Post-PR survey completeness check
    st.subheader("Post-PR survey status")
    if participant_id:
        with st.spinner("Checking post-PR responses..."):
            missing_result = get_missing_post_pr_surveys(participant_id)

        if missing_result['success']:
            missing = missing_result.get('missing', [])
            if not missing:
                st.success("All completed issues have post-PR responses saved.")
            else:
                st.warning(f"{len(missing)} completed issue(s) still need post-PR responses.")
                for item in missing:
                    issue_id = item.get('issue_id')
                    issue_url = item.get('issue_url') or f"Issue {issue_id}"
                    reason = item.get('reason', 'missing data')
                    fields = item.get('missing_fields', [])
                    details = f"Missing: {', '.join(fields)}" if fields else reason
                    st.write(f"- {issue_url}: {details}")
        else:
            st.error(f"Unable to check post-PR status: {missing_result.get('error')}")
    else:
        st.info("Enter your participant ID to check post-PR survey status.")

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.divider()

    st.subheader("Update a merged/closed PR")
    st.markdown("""
    If you have discussed your pull request with reviewers and it has been **merged or closed**,
    you can update the status of a previous PR here and submit your screen recorder data.
    """)
    if st.button("Update PR"):
        from survey_utils import clear_form_cache_between_issues
        clear_form_cache_between_issues()
        st.session_state['page'] = 18  # PR closed update page
        st.rerun()
