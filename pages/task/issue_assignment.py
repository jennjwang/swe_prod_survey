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
    request_different_issue
)


def issue_assignment_page():
    """Display the issue assignment page."""

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

    page_header(
        "Issue Assignment",
        "You will be randomly assigned 4 issues to work on from your repository."
    )

    # Get participant info from session state
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
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

    # Check if participant already has all 4 issues assigned
    if participant_id:
        check_result = check_all_issues_assigned(participant_id)

        if check_result['success'] and not check_result['all_assigned']:
            # First time - assign all 4 issues at once
            st.markdown("""
                <p style='font-size:18px; margin-bottom: 1.5rem;'>
                You're welcome to seek clarification and engage in discussion with the project maintainer just as you would in a 
                open-source development.
                </p>
                """, unsafe_allow_html=True)

            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Get My Assignments", key="assign_all", type="primary", use_container_width=True):
                    with st.spinner('Assigning your issues...'):
                        assign_result = assign_all_issues_to_participant(participant_id, assigned_repo)

        elif check_result['success'] and check_result['all_assigned']:
            # Get next issue in sequence
            next_result = get_next_issue_in_sequence(participant_id)

            if next_result['success'] and next_result['issue']:
                # Show next issue
                issue = next_result['issue']
                sequence = next_result['sequence']
                total_completed = next_result['total_completed']

                # Progress indicator
                st.warning(f"**Progress:** {total_completed} of 4 issues completed")

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
                    (e.g., "I'd like to work on this issue"). This follows standard open-source
                    contribution practices.
                    </p>
                    """, unsafe_allow_html=True)

                # Checkbox to confirm they've claimed the issue
                claimed_issue = st.checkbox(
                    "I have claimed this issue in the discussion",
                    key=f"claimed_issue_{issue_id}"
                )

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
                # All issues complete
                st.success("You have completed all your assigned issues!")
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
