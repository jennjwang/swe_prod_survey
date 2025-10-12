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
                Thank you for completing this issue and survey! You have completed {completed_count} of {total_count} assigned issues.
                </p>
                """, unsafe_allow_html=True)

            st.success("This issue's survey completed successfully!")

            # Show next steps based on whether post-exp1 is completed
            if not post_exp1_completed:
                st.markdown("""
                    <div style='background-color: #e3f2fd; border-left: 4px solid #2196F3; padding: 1.5rem; margin: 2rem 0; border-radius: 4px;'>
                        <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem; color: #1565c0;'>
                        Next: Questions About This Issue
                        </p>
                        <p style='font-size:16px; margin: 0; color: #555;'>
                        Before moving to your next issue, we have a few questions about your experience with this one.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # Continue button to post-exp1
                st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("Continue", key="completion_has_more_continue", type="primary", use_container_width=True):
                        st.session_state['page'] = 15  # AI usage page
                        st.rerun()
            else:
                st.info("""
                    **Next Steps:**
                    You have more issues assigned to you. Please return to the issue assignment page to continue with your next issue.
                """)
        else:
            page_header(
                "All Issues Complete!",
                "You have completed all your assigned issues."
            )

            st.success(f"✅ You have completed {total_count} of {total_count} assigned issues!")

            st.markdown("""
                <div style='background-color: #e8f5e9; border-left: 4px solid #4CAF50; padding: 1.5rem; margin: 2rem 0; border-radius: 4px;'>
                    <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem; color: #2e7d32;'>
                    Next Step: Post-Experiment 1 Questions
                    </p>
                    <p style='font-size:16px; margin-bottom: 0.5rem; color: #555;'>
                    Now we'll ask you a few questions about your experience across the entire experiment.
                    </p>
                    <p style='font-size:16px; margin: 0; color: #555;'>
                    This will help us understand your overall perspective on using AI tools for development.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Continue button
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("Continue", key="completion_continue", type="primary", use_container_width=True):
                    # Check if post-exp1 completed
                    if not post_exp1_completed:
                        # Go to AI usage questions first
                        st.session_state['page'] = 15  # AI usage page
                    else:
                        # Already completed post-exp1, go to thank you
                        st.session_state['page'] = 19  # Thank you page
                    st.rerun()
    
    # Display participant details (common to both scenarios)
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    assigned_repo = st.session_state['survey_responses'].get('assigned_repository', '')
    assigned_issue_url = st.session_state['survey_responses'].get('issue_url', '')
    pr_url = st.session_state['survey_responses'].get('pr_url', '')
    time_estimation = st.session_state['survey_responses'].get('time_estimation', '')
    
    # Show key information
    st.markdown("---")
    st.markdown("""
        <p style='font-size:18px; font-weight: 600; margin-bottom: 1rem'>
        Your Assignment Details:
        </p>
        """, unsafe_allow_html=True)
    
    if participant_id:
        st.info(f"**Participant ID:** {participant_id}")
    
    if assigned_repo:
        st.info(f"**Assigned Repository:** {assigned_repo}")
    
    # if assigned_issue_url:
    #     st.info(f"**Assigned Issue:** [{assigned_issue_url}]({assigned_issue_url})")
    
    # if time_estimation:
    #     st.info(f"**Estimated Time:** {time_estimation}")
    
    if pr_url:
        st.info(f"**Pull Request:** [{pr_url}]({pr_url})")
    # Closing message
    st.markdown("---")
    st.markdown("""
        <div>
            <p style='font-size:16px; color: #666'>
            If you have any questions or concerns, please contact the study administrator.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Optional: View all responses (for debugging/transparency)
    with st.expander("View all your responses"):
        st.json(st.session_state['survey_responses'])


def already_completed_page():
    """Redirect to completion page with already_completed flag."""
    st.session_state['completion_type'] = 'already_completed'
    completion_page()
