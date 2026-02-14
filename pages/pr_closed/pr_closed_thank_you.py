"""
Thank you page shown after completing PR closed survey responses.
"""

import streamlit as st
from survey_components import page_header
from survey_data import get_supabase_client


def pr_closed_thank_you_page():
    """Display thank you page after PR closed survey completion."""

    # Check if all PR-closed surveys are complete
    participant_id = st.session_state['survey_responses'].get('participant_id', '')
    supabase_client = get_supabase_client()

    if supabase_client and participant_id:
        try:
            # Get total number of assigned issues
            all_assigned = supabase_client.table('repo-issues')\
                .select('issue_id')\
                .ilike('participant_id', participant_id)\
                .execute()
            total_assigned = len(all_assigned.data) if all_assigned.data else 0

            # Get number of merged or closed issues
            closed_issues = supabase_client.table('repo-issues')\
                .select('issue_id')\
                .ilike('participant_id', participant_id)\
                .or_('is_merged.eq.true,is_closed.eq.true')\
                .execute()
            total_closed = len(closed_issues.data) if closed_issues.data else 0

            # Get number of completed pr-closed surveys (where learn_4 is not null)
            completed_surveys = supabase_client.table('pr-closed')\
                .select('issue_id')\
                .ilike('participant_id', participant_id)\
                .not_.is_('learn_4', 'null')\
                .execute()

            completed_count = len(completed_surveys.data) if completed_surveys.data else 0

            # All complete only if ALL assigned issues are merged/closed AND all surveys done
            all_prs_closed = total_assigned > 0 and total_closed >= total_assigned
            all_surveys_complete = all_prs_closed and completed_count >= total_closed

            print(f"DEBUG pr_closed_thank_you: Total assigned: {total_assigned}, Total closed: {total_closed}, Surveys completed: {completed_count}")
            print(f"DEBUG pr_closed_thank_you: All PRs closed: {all_prs_closed}, All surveys complete: {all_surveys_complete}")

            # If all surveys are complete, route to end of study questions
            if all_surveys_complete:
                # Check if post-study survey is already complete
                existing = supabase_client.table('post-study')\
                    .select('participant_id, ai_responsibility, value_reading_issue')\
                    .ilike('participant_id', participant_id)\
                    .not_.is_('ai_responsibility', 'null')\
                    .not_.is_('value_reading_issue', 'null')\
                    .execute()

                # If post-study already complete, go to final thank you (26)
                # Otherwise, go to end of study survey (25)
                if existing.data and len(existing.data) > 0:
                    st.session_state['page'] = 26  # final_thank_you_page
                else:
                    st.session_state['page'] = 25  # end_of_study_thank_you_page
                st.rerun()
                return

        except Exception as e:
            print(f"Error checking survey completion status: {e}")

    page_header(
        "Thank You!",
        "Thank you for participating in the code review process for this PR."
    )

    st.success("Your responses about the code review process have been recorded")

    # Buttons to navigate
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Back to Issue Status", type="secondary", use_container_width=True):
            from survey_utils import clear_form_cache_between_issues
            clear_form_cache_between_issues()
            st.session_state['page'] = 10  # Back to issue completion page
            st.rerun()

    with col2:
        if st.button("Update Another PR", type="secondary", use_container_width=True):
            from survey_utils import clear_form_cache_between_issues
            clear_form_cache_between_issues()
            st.session_state['page'] = 18  # Back to update issue page
            st.rerun()

    
