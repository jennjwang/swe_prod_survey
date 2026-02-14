"""
PR closed update page for participants who have follow-up information.
"""

import streamlit as st
from survey_components import page_header
from survey_data import get_supabase_client


def update_issue_page():
    # Check if there's an incomplete PR closed survey in progress
    selected_issue = st.session_state.get('pr_closed_selected_issue')
    if selected_issue:
        # Check which questions have been completed
        has_collaboration = 'pr_closed_collaboration' in st.session_state
        has_engagement = 'pr_closed_engagement' in st.session_state

        # Route to the first incomplete page
        if not has_collaboration:
            st.session_state['page'] = 19  # collaboration_questions_page
            st.rerun()
            return
        elif not has_engagement:
            st.session_state['page'] = 20  # engagement_questions_page
            st.rerun()
            return
        else:
            # Both collaboration and engagement are done, go to learning outcomes
            st.session_state['page'] = 22  # learning_outcomes_questions_page
            st.rerun()
            return

    page_header(
        "Update Merged/Closed Pull Request",
        "Once your pull request has been <i>merged or closed</i>, please submit your data below. "
        "These files should capture your engagement with the reviewer, including reviewing their feedback and making changes to your code if needed."
    )

    # Get participant ID from session state
    participant_id = st.session_state['survey_responses'].get('participant_id', '')

    if not participant_id:
        st.error("⚠️ Participant ID not found. Please return to the main survey.")
        if st.button("Back to Issue Status"):
            st.session_state['page'] = 10
            st.rerun()
        return

    # Fetch all completed issues for this participant
    supabase_client = get_supabase_client()
    if not supabase_client:
        st.error("⚠️ Database connection error. Please try again later.")
        return

    try:
        # Fetch total assigned issues for this participant
        assigned_result = supabase_client.table('repo-issues')\
            .select('issue_id')\
            .ilike('participant_id', participant_id)\
            .execute()
        total_assigned = len(assigned_result.data) if assigned_result.data else 0

        # Fetch issues that are either merged or closed
        result = supabase_client.table('repo-issues')\
            .select('*')\
            .ilike('participant_id', participant_id)\
            .or_('is_merged.eq.true,is_closed.eq.true')\
            .execute()

        all_completed_issues = result.data if result.data else []

        # Fetch issues that already have pr-closed surveys completed (learn_4 is not null)
        pr_closed_result = supabase_client.table('pr-closed')\
            .select('issue_id, learn_4')\
            .ilike('participant_id', participant_id)\
            .not_.is_('learn_4', 'null')\
            .execute()
        completed_survey_issue_ids = {int(item['issue_id']) for item in pr_closed_result.data} if pr_closed_result.data else set()

        # Filter out issues that already have completed surveys
        completed_issues = [issue for issue in all_completed_issues if issue.get('issue_id') not in completed_survey_issue_ids]
        print(f'completed_issues: {completed_issues}')
        print(f'completed_survey_issue_ids: {completed_survey_issue_ids}')

        # Check if all PRs are closed and all pr_closed surveys are done
        total_reviewed_prs = len(all_completed_issues)
        total_completed_surveys = len(completed_survey_issue_ids)
        # All PRs complete only if ALL assigned issues are merged/closed AND all surveys done
        all_prs_closed = total_assigned > 0 and total_reviewed_prs >= total_assigned
        all_pr_surveys_complete = all_prs_closed and total_completed_surveys >= total_reviewed_prs

        print(f'DEBUG: Total assigned: {total_assigned}, Total reviewed PRs: {total_reviewed_prs}, Total completed surveys: {total_completed_surveys}')
        print(f'DEBUG: All PRs closed: {all_prs_closed}, All surveys complete: {all_pr_surveys_complete}')

        # If all PRs are closed and all pr_closed surveys are filled, route to end of study questions
        if all_pr_surveys_complete:
            print("DEBUG: All PRs closed and all pr_closed surveys complete, checking post-study status")
            try:
                post_study_result = supabase_client.table('post-study')\
                    .select('participant_id, ai_responsibility, value_reading_issue')\
                    .ilike('participant_id', participant_id)\
                    .not_.is_('ai_responsibility', 'null')\
                    .not_.is_('value_reading_issue', 'null')\
                    .execute()

                # If post-study already complete, go to final thank you (26)
                # Otherwise, go to end of study survey (25)
                if post_study_result.data and len(post_study_result.data) > 0:
                    print("DEBUG: Post-study complete, routing to final thank you")
                    st.session_state['page'] = 26  # final_thank_you_page
                else:
                    print("DEBUG: Post-study not complete, routing to end of study survey")
                    st.session_state['page'] = 25  # end_of_study_thank_you_page
                st.rerun()
                return
            except Exception as e:
                print(f"Error checking post-study status: {e}")
                # On error, route to end of study survey
                # st.session_state['page'] = 25
                # st.rerun()
                return

    except Exception as e:
        st.error(f"⚠️ Error fetching completed issues: {e}")
        print(f"Error fetching completed issues: {e}")
        return

    # Check if there are any completed issues
    if not completed_issues:
        st.info("You don't have any closed/merged PRs ready to update. Please continue your discussion with reviewers and return to this page when you have a PR that has been merged or closed.")
        if st.button("Back to Issue Status"):
            st.session_state['page'] = 10
            st.rerun()
        return

    # Display list of completed PRs for selection
    st.subheader("Select a PR to Update")
    st.write("Choose the PR you want to submit code review data for:")

    # Create a list of PR options for the selectbox
    pr_options = []
    for pr in completed_issues:
        issue_url = pr.get('issue_url', 'Unknown')
        pr_url = pr.get('pr_url', 'Unknown')
        issue_id = pr.get('issue_id')
        last_digit = pr_url.rstrip('/').split('/')[-1]

        # Format the display text
        label = f"PR #{last_digit} - {pr_url}"

        pr_options.append((label, pr))

    # Calculate a valid index for the selectbox
    saved_index = st.session_state.get('selected_update_pr_index', 0)
    valid_index = max(0, min(saved_index, len(pr_options) - 1))

    selected_label = st.selectbox(
        "Select PR:",
        options=range(len(pr_options)),
        format_func=lambda i: pr_options[i][0],
        index=valid_index,
        key="pr_selector",
        label_visibility="collapsed"
    )

    # Update session state with selected index
    st.session_state['selected_update_pr_index'] = selected_label
    selected_pr = pr_options[selected_label][1]
    selected_issue_id = selected_pr.get('issue_id')

    # # Display selected issue details
    st.divider()
    # st.info(f"**Selected Issue:** [{selected_issue.get('issue_url')}]({selected_issue.get('issue_url')})")

    # Data upload section
    # st.markdown("<div style='margin-top: rem;'></div>", unsafe_allow_html=True)
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
    st.warning("**Large files (>500MB):** If your recording is too large, please use **[this Google Form](https://forms.gle/GmcmX9kyTsQPXGMA9)** instead.")
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
            "Submit Data",
            key="submit_update",
            type="primary",
        )

    if submit_button:
        # Validate that at least one file is uploaded
        if not specstory_upload and not screenrec_upload:
            st.error("Please upload at least one file (SpecStory folder or Screen Recorder data).")
            return

        # Re-validate file size at submit time — do not allow submission of large files
        if specstory_upload and (specstory_upload.size is None or specstory_upload.size > max_file_size_bytes):
            st.error(f"⚠️ SpecStory file is too large. Submission not allowed. Please keep uploads under {max_file_size_mb} MB or use the Google Form for larger files.")
            return
        if screenrec_upload and (screenrec_upload.size is None or screenrec_upload.size > max_file_size_bytes):
            st.error(f"⚠️ Screen recorder file is too large. Submission not allowed. Please keep uploads under {max_file_size_mb} MB or use the Google Form for larger files.")
            return

        def _ok_to_upload(upload):
            return upload and upload.size is not None and upload.size <= max_file_size_bytes

        # Upload files to Drive only when size is valid (never submit large files)
        try:
            from pages.task.drive_upload import upload_to_drive_in_subfolders, sanitize_filename
            folder_id = st.secrets.get('GDRIVE_FOLDER_ID', '')

            if not folder_id:
                st.error("⚠️ Drive folder not configured. Please contact the study administrator.")
                return

            with st.spinner('Uploading your files...'):
                participant_folder = sanitize_filename(participant_id) if participant_id else "unknown_participant"
                issue_folder = f"issue_{selected_issue_id}_update"
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

            st.success("Files uploaded successfully!")

            # Store selected issue in session state for subsequent pages
            st.session_state['pr_closed_selected_issue'] = selected_pr

            # Clear form cache before transitioning to next issue/survey
            from survey_utils import clear_form_cache_between_issues
            clear_form_cache_between_issues()

            # Navigate to collaboration questions
            st.session_state['page'] = 19  # collaboration_questions_page
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ Upload failed: {e}")
            print(f"Upload error: {e}")
            return

    st.divider()

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col1:
        if st.button("Back to Issue Status"):
            from survey_utils import clear_form_cache_between_issues
            clear_form_cache_between_issues()
            st.session_state['page'] = 10  # Return to issue completion page
            st.rerun()

    with col3:
        if st.button("Continue", key="continue_to_survey"):
            # Store selected issue in session state
            st.session_state['pr_closed_selected_issue'] = selected_pr

            # Check database for existing survey progress
            try:
                pr_closed_data = supabase_client.table('pr-closed')\
                    .select('collab_1, engage_1, learn_1')\
                    .ilike('participant_id', participant_id)\
                    .eq('issue_id', selected_issue_id)\
                    .execute()

                if pr_closed_data.data and len(pr_closed_data.data) > 0:
                    record = pr_closed_data.data[0]
                    has_collab = record.get('collab_1') is not None
                    has_engage = record.get('engage_1') is not None
                    has_learn = record.get('learn_1') is not None

                    # Route to first incomplete page
                    if not has_collab:
                        st.session_state['page'] = 19  # collaboration_questions_page
                    elif not has_engage:
                        st.session_state['page'] = 20  # engagement_questions_page
                    elif not has_learn:
                        st.session_state['page'] = 22  # learning_outcomes_questions_page
                    else:
                        # All sections complete
                        st.session_state['page'] = 23  # pr_closed_thank_you_page
                else:
                    # No existing record, start from beginning
                    st.session_state['page'] = 19  # collaboration_questions_page
            except Exception as e:
                print(f"Error checking survey progress: {e}")
                # Default to collaboration questions if error
                st.session_state['page'] = 19

            from survey_utils import clear_form_cache_between_issues
            clear_form_cache_between_issues()
            st.rerun()
