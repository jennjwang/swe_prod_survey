"""
Issue assignment page for the survey.
"""

import streamlit as st
from survey_components import page_header
from survey_utils import save_and_navigate
from survey_data import (
    assign_all_issues_to_participant,
    check_all_issues_assigned,
    get_next_issue_in_sequence,
    request_different_issue,
    get_participant_progress,
    REQUIRED_ISSUE_COUNT
)


def issue_assignment_page():
    """Display the issue assignment page."""

    participant_id = st.session_state['survey_responses'].get('participant_id', '')

    # Check if participant has an issue that needs survey completion
    # This prevents them from being assigned their next issue before finishing the survey
    if participant_id:
        from survey_data import get_issue_needing_survey
        survey_check = get_issue_needing_survey(participant_id)

        if survey_check['success'] and survey_check['issue']:
            issue = survey_check['issue']
            issue_id = issue['issue_id']
            nasa_tlx_1 = survey_check.get('nasa_tlx_1')
            ai_code_quality = survey_check.get('ai_code_quality')
            using_ai = survey_check.get('using_ai', False)

            # Restore issue info to session state
            st.session_state['survey_responses']['issue_id'] = issue_id
            st.session_state['survey_responses']['issue_url'] = issue.get('issue_url', '')
            st.session_state['survey_responses']['current_issue_using_ai'] = using_ai

            # Determine which page to route to based on what's completed
            if nasa_tlx_1 is None:
                # NASA-TLX not done yet, go there first
                print(f"DEBUG: Issue {issue_id} NASA-TLX not done, redirecting to page 12")
                st.session_state['page'] = 12  # post_issue_questions_page
            elif using_ai and ai_code_quality is None:
                # AI user still needs reflection questions
                print(f"DEBUG: Issue {issue_id} AI reflection not done, redirecting to page 13")
                st.session_state['page'] = 13  # post_issue_reflection_page
            else:
                # All done, go to reflection page (final step)
                print(f"DEBUG: Issue {issue_id} survey done, redirecting to page 13")
                st.session_state['page'] = 13  # post_issue_reflection_page
            st.rerun()
            return

    if participant_id:
        checklist_state = st.session_state['survey_responses'].get('checklist_completed')
        if checklist_state is not True:
            progress_result = get_participant_progress(participant_id)
            if progress_result.get('success'):
                progress = progress_result.get('progress', {})
                checklist_done = progress.get('checklist_completed') is True
                st.session_state['survey_responses']['checklist_completed'] = checklist_done
                if not checklist_done:
                    st.info("Please finish the setup checklist before continuing to your issue assignments.")
                    st.session_state['page'] = 6  # setup checklist page
                    st.rerun()

    # Check if we need to show AI condition acknowledgment
    if st.session_state.get('show_ai_condition', False):
        using_ai = st.session_state.get('ai_condition_value', False)

        page_header(
            "AI Condition Assignment",
            "Please read and acknowledge the following instructions for this issue."
        )

        if using_ai:
            st.success("**You MAY use AI tools for this issue.**")
            st.markdown("""
                <p style='font-size:18px; margin-top: 1rem; margin-bottom: 1rem;'>
                You are <strong>encouraged</strong> to use AI assistants to help you complete this task, including:
                </p>
                <ul style='font-size:16px; margin-left: 2rem;'>
                    <li>ChatGPT, Claude, Gemini, or similar AI chatbots</li>
                    <li>GitHub Copilot, Cursor, or similar AI code assistants</li>
                    <li>Any other AI-powered development tools</li>
                </ul>
                """, unsafe_allow_html=True)
        else:
            st.warning("**You should NOT use AI tools for this issue.**")
            st.markdown("""
                <p style='font-size:18px; margin-top: 1rem; margin-bottom: 1rem;'>
                Please complete this task <strong>without</strong> using AI assistants, including:
                </p>
                <ul style='font-size:16px; margin-left: 2rem;'>
                    <li>ChatGPT, Claude, Gemini, or similar AI chatbots</li>
                    <li>GitHub Copilot, Cursor, or similar AI coding agents</li>
                    <li>Any other AI-powered development tools</li>
                </ul>
                """, unsafe_allow_html=True)

        st.divider()

        # Acknowledgment button
        col1, col2 = st.columns([1, 1])
        with col1:
            acknowledge_text = "I understand" if using_ai else "I understand and will NOT use AI tools"
            if st.button(acknowledge_text, key="acknowledge_ai", type="primary", use_container_width=True):
                # Clear the acknowledgment flag
                st.session_state['show_ai_condition'] = False
                st.session_state['ai_condition_value'] = None
                # Navigate to issue completion page
                st.session_state['page'] = 10  # issue_completion_page
                st.rerun()

        return

    issue_word = "issue" if REQUIRED_ISSUE_COUNT == 1 else "issues"
    page_header(
        "Issue Assignment",
        f"You will be randomly assigned {REQUIRED_ISSUE_COUNT} {issue_word} to work on from your repository."
    )

    # Get participant info from session state
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')
    repo_url = st.session_state['survey_responses'].get('repository_url', '')

    # Display context
    # if participant_id:
    #     st.info(f"**Participant ID:** {participant_id}")
    if assigned_repo:
        if repo_url:
            st.info(f"**Assigned Repository:** [{assigned_repo}]({repo_url})")
        else:
            st.info(f"**Assigned Repository:** {assigned_repo}")

    # st.divider()

    # Check if participant already has the required issues assigned
    if participant_id:
        check_result = check_all_issues_assigned(participant_id)

        if check_result['success']:
            assigned_count = check_result.get('count', 0)
            has_assignments = assigned_count > 0
            limited_inventory = assigned_count < REQUIRED_ISSUE_COUNT

            if not has_assignments:
                # First time - assign available issue(s)
                st.markdown("""
                    <p style='font-size:18px; margin-bottom: 1.5rem;'>
                    We want this to feel like the open source development process, so please don’t hesitate to seek clarification and engage in discussion with the project maintainer.
                    </p>
                    """, unsafe_allow_html=True)

                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button("Get My Assignments", key="assign_all", type="primary", use_container_width=True):
                        with st.spinner(f"Assigning your {issue_word}..."):
                            assign_result = assign_all_issues_to_participant(participant_id, assigned_repo)
                            if assign_result.get('success'):
                                st.rerun()
                            else:
                                st.error(assign_result.get('error', 'Unable to assign issues.'))
            else:
                if limited_inventory:
                    issue_noun = "issue" if assigned_count == 1 else "issues"
                    repo_display = assigned_repo or "your repository"
                    st.warning(f"Only {assigned_count} {issue_noun} were available for {repo_display}. We’ll assign additional issues automatically once more become available.")

                # Get next issue in sequence
                next_result = get_next_issue_in_sequence(participant_id)

                if next_result['success'] and next_result['issue']:
                    # Show next issue
                    issue = next_result['issue']
                    sequence = next_result['sequence']
                    total_completed = next_result.get('total_completed', 0)
                    total_assigned = next_result.get('total_assigned', assigned_count)

                    # Progress indicator based on actual assigned issues
                    completed_display = min(total_completed, total_assigned)
                    progress_noun = "issue" if total_assigned == 1 else "issues"
                    st.warning(f"**Progress:** {completed_display} of {total_assigned} {progress_noun} completed")

                    # Show issue details
                    issue_url = issue.get('issue_url', '') or issue.get('url', '')
                    issue_id = issue.get('issue_id', '')

                    st.markdown("""
                        <p style='font-size:18px; margin-top: 1rem; margin-bottom: 1rem;'>
                        <strong>Your Next Issue:</strong>
                        </p>
                        """, unsafe_allow_html=True)
                    
                    if issue_url:
                        st.markdown(f"""
                            <p style='font-size:18px;'>
                            <a href="{issue_url}" target="_blank">{issue_url}</a>
                            </p>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning(f"Issue ID: {issue_id} (URL not available)")
                        print(f"DEBUG: Issue data: {issue}")

                    st.divider()

                    # Instructions to claim the issue
                    st.markdown("""
                        <p style='font-size:18px; margin-top: 1rem; margin-bottom: 1rem;'>
                        <strong>Before you start:</strong>
                        </p>
                        """, unsafe_allow_html=True)

                    st.markdown("""
                        <p style='font-size:16px; margin-bottom: 1rem;'>
                        Please go to the issue discussion and claim the issue by leaving a comment
                        (e.g., "I'd like to work on this issue").
                        This follows standard open-source
                        contribution practices.
                        </p>
                        """, unsafe_allow_html=True)

                    # Checkbox to confirm they've claimed the issue
                    claimed_issue = st.checkbox(
                        "I have claimed this issue in the discussion",
                        key=f"claimed_issue_{issue_id}"
                    )

                    # Warning to not work on the issue yet - only show if checkbox is checked
                    if claimed_issue:
                        st.warning("""
                        ⚠️ **Important:** Please do not work on the issue yet.
                        On the next two pages, you will estimate the time needed to complete this issue and be assigned an AI condition.
                        Only begin working after completing these steps.
                        """)

                    # Navigation button
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        if st.button("Start This Issue", key="start_issue", type="primary", use_container_width=True, disabled=not claimed_issue):
                            # Save issue info to session state
                            st.session_state['survey_responses']['assigned_issue'] = issue
                            st.session_state['survey_responses']['issue_url'] = issue_url
                            st.session_state['survey_responses']['issue_id'] = issue['issue_id']

                            # Reset post-exp1 completion flag for new issue
                            st.session_state['post_exp1_completed'] = False

                            # Save AI condition (will be shown after time estimation)
                            using_ai = issue.get('using_ai', False)
                            st.session_state['survey_responses']['current_issue_using_ai'] = using_ai

                            # Go directly to time estimation page
                            st.session_state['page'] = 9  # time_estimation_page
                            st.rerun()

                    st.divider()

                    # Note about requesting a different issue
                    st.caption("If you would like to request a different issue, please contact jennjwang@stanford.edu with a justification. We will facilitate the swap if it is well-justified.")

                elif next_result['success'] and next_result['issue'] is None:
                    # All assigned issues complete
                    total_assigned = next_result.get('total_assigned', assigned_count)
                    st.success("You have completed all assigned issues!")
                    if limited_inventory:
                        completed_noun = "issue" if total_assigned == 1 else "issues"
                        st.info(f"You were assigned {total_assigned} {completed_noun} because only those were available in the repository.")
                    st.markdown("""
                        <p style='font-size:18px; margin-top: 1rem;'>
                        Thank you for your participation. Please proceed to the final survey questions.
                        </p>
                        """, unsafe_allow_html=True)

                else:
                    st.error(f"⚠️ Error retrieving next issue: {next_result.get('error', 'Unknown error')}")

        else:
            st.error("⚠️ Error checking issue assignments. Please contact the study administrator.")
    else:
        st.warning("Please complete the pre-study survey first to receive your issue assignments.")
