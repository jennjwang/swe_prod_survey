"""
Unified completion page for the survey.
Handles both regular completion and already-completed scenarios.
Checks if participant has more issues to complete.
"""

import streamlit as st
from survey_components import page_header
from survey_data import check_participant_has_more_issues


def completion_page():
    """Display the survey completion page."""
    # Get participant ID
    participant_id = st.session_state['survey_responses'].get('participant_id', '')

    # Refresh post-exp1 completion status from database if not already set
    if participant_id and not st.session_state.get('post_exp1_completed', False):
        try:
            from survey_data import check_post_exp1_completed
            post_exp1_status = check_post_exp1_completed(participant_id)
            if post_exp1_status.get('success') and post_exp1_status.get('completed'):
                st.session_state['post_exp1_completed'] = True
        except Exception as e:
            print(f"Error checking post-exp1 completion: {e}")

    # If any completed issue is missing post-PR responses, redirect to those pages first
    if participant_id:
        from survey_data import get_issue_needing_survey
        survey_check = get_issue_needing_survey(participant_id)
        if survey_check['success'] and survey_check['issue']:
            issue = survey_check['issue']
            issue_id = issue['issue_id']
            nasa_tlx_1 = survey_check.get('nasa_tlx_1')
            ai_code_quality = survey_check.get('ai_code_quality')
            using_ai = survey_check.get('using_ai', False)

            st.session_state['survey_responses']['issue_id'] = issue_id
            st.session_state['survey_responses']['issue_url'] = issue.get('issue_url', '')
            st.session_state['survey_responses']['current_issue_using_ai'] = using_ai

            if nasa_tlx_1 is None:
                st.session_state['page'] = 12  # post_issue_questions_page
            elif using_ai and ai_code_quality is None:
                st.session_state['page'] = 13  # post_issue_reflection_page
            else:
                st.session_state['page'] = 13  # post_issue_reflection_page
            st.rerun()
            return

    # Check if participant has completed post-exp1 questions yet
    post_exp1_completed = st.session_state.get('post_exp1_completed', False)

    # Check if this is a return visit (already completed)
    is_return_visit = st.session_state.get('completion_type') == 'already_completed'

    if is_return_visit:
        # Already completed scenario
        page_header(
            "Survey Completed",
            "You have already completed the PR survey responses."
        )

        st.markdown("""
            <div>
                <p style='font-size:16px; color: #666;'>
                No further action is required from you at this time.
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Fresh completion scenario
        # Check if there are more issues
        has_more = False
        completed_count = 0
        total_count = 0
        if participant_id:
            result = check_participant_has_more_issues(participant_id)
            if result['success']:
                has_more = result['has_more_issues']
                completed_count = result['completed_count']
                total_count = result['total_count']

        if has_more:
            st.header("Issue Complete!")

            st.markdown(f"""
                <p style='font-size:20px; margin-bottom: 2rem;'>
                Thank you for completing this issue and survey!
                </p>
                """, unsafe_allow_html=True)

            # st.success("This issue's survey completed successfully!")

            st.info(
                f"You have completed {completed_count} of {total_count} assigned issues."
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Continue to Next Issue", key="completion_continue", type="primary", use_container_width=True):
                    st.session_state['page'] = 8  # Issue assignment page
                    st.rerun()
        else:
            page_header(
                "All Issues Complete!",
                "You have completed all your assigned issues."
            )

            # st.success(f"You have completed {total_count} of {total_count} assigned issues!")

            st.markdown("""
                <div style='background-color: #e8f5e9; border-left: 4px solid #4CAF50; padding: 1.5rem; margin: 2rem 0; border-radius: 4px;'>
                    <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem; color: #2e7d32;'>
                    Next Step: End of Experiment 1
                    </p>
                    <p style='font-size:16px; margin-bottom: 0.5rem; color: #555;'>
                    Now we'll ask you a few questions about your experience across the entire first experiment.
                    </p>
                    <p style='font-size:16px; margin: 0; color: #555;'>
                    This will help us understand your overall perspective on using AI tools for development.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Continue button - left aligned at the end
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            if st.button("Continue", key="completion_continue", type="primary"):
                # Check if post-exp1 completed
                if not post_exp1_completed:
                    # Go to study validation questions first
                    st.session_state['page'] = 14  # Study validation page (page 14)
                else:
                    # Already completed post-exp1, go to thank you
                    st.session_state['page'] = 17  # Thank you page (page 17)
                st.rerun()
    
    # Display participant details (common to both scenarios)
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')
    assigned_issue_url = st.session_state['survey_responses'].get('issue_url', '')
    pr_url = st.session_state['survey_responses'].get('pr_url', '')
    time_estimation = st.session_state['survey_responses'].get('time_estimation', '')
    
    # # Show key information
    # st.markdown("---")
    # st.markdown("""
    #     <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem'>
    #     Your Assignment Details:
    #     </p>
    #     """, unsafe_allow_html=True)
    
    # if participant_id:
    #     st.info(f"**Participant ID:** {participant_id}")
    
    # if assigned_repo:
    #     st.info(f"**Assigned Repository:** {assigned_repo}")
    
    # if assigned_issue_url:
    #     st.info(f"**Assigned Issue:** [{assigned_issue_url}]({assigned_issue_url})")
    
    # if time_estimation:
    #     st.info(f"**Estimated Time:** {time_estimation}")
    
    # if pr_url:
    #     st.info(f"**Pull Request:** [{pr_url}]({pr_url})")
    # # Closing message
    # st.markdown("---")
    # st.markdown("""
    #     <div>
    #         <p style='font-size:16px; color: #666'>
    #         If you have any questions or concerns, please contact the study administrator.
    #         </p>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # # Optional: View all responses (for debugging/transparency)
    # with st.expander("View all your responses"):
    #     st.json(st.session_state['survey_responses'])


def already_completed_page():
    """Redirect to completion page with already_completed flag."""
    st.session_state['completion_type'] = 'already_completed'
    completion_page()
