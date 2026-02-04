"""
Participant ID page for the survey.
"""

import streamlit as st
from survey_components import page_header, text_input_question
from survey_utils import save_and_navigate, next_page
from survey_data import (
    validate_participant_id,
    get_participant_progress,
    get_repository_assignment,
    REQUIRED_ISSUE_COUNT
)


def participant_id_page():
    """Display the participant ID input page."""
    page_header(
        "The Ripple Effects of AI in Software Development",
        "Please enter your email to begin the survey."
    )

    # Load previous participant ID if it exists
    previous_participant_id = st.session_state['survey_responses'].get('participant_id', '')

    # Participant ID input
    participant_id = text_input_question(
        "Email:",
        "participant_id_input",
        previous_participant_id,
        placeholder="Enter your email"
    )
    
    # Navigation - hide back button since this is the first page
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    next_clicked = st.button("Next", key="participant_id_next")
    
    if next_clicked:
        # Basic validation first
        if not participant_id or not participant_id.strip():
            st.error("Please enter your email to proceed.")
        else:
            # Validate against database
            with st.spinner('Validating email...'):
                validation_result = validate_participant_id(participant_id)
            
            if validation_result['valid']:
                # ID is valid, save it
                st.session_state['survey_responses']['participant_id'] = participant_id
                
                # Check progress to see if they should skip ahead
                with st.spinner('Checking your progress...'):
                    progress_result = get_participant_progress(participant_id)
                
                if progress_result['success']:
                    progress = progress_result['progress']
                    
                    # Load pre-study data if it exists
                    if progress['pre_study_completed'] and progress['pre_study_data']:
                        pre_data = progress['pre_study_data']
                        checklist_completed = pre_data.get('checklist_completed') is True
                        st.session_state['survey_responses'].update({
                            'professional_experience': pre_data.get('professional_experience'),
                            'assigned_repository': pre_data.get('assigned_repository'),
                            'repository_url': pre_data.get('repository_url'),
                            'forked_repository_url': pre_data.get('forked_repository_url'),
                            'code_experience': pre_data.get('code_experience'),
                            'checklist_completed': checklist_completed,
                            'ai_experience': {
                                'llm_hours': pre_data.get('ai_experience_llm_hours'),
                                'agent_hours': pre_data.get('ai_agent_experience_hours'),
                            }
                        })
                        st.session_state['pre_study_saved'] = True

                    # Note: Issue data is loaded later based on get_next_issue_in_sequence()
                    # to ensure we load the correct next incomplete issue, not just the first issue

                    # Debug output
                    print(f"DEBUG: Progress data: {progress}")
                    # print(f"DEBUG: pre_study_completed = {progress['pre_study_completed']}")
                    # print(f"DEBUG: issue_assigned = {progress['issue_assigned']}")
                    # print(f"DEBUG: issue_completed = {progress['issue_completed']}")
                    
                    # Route based on progress - CHECK PRE-STUDY FIRST
                    checklist_completed = progress.get('checklist_completed', False)

                    if progress['pre_study_completed'] and not checklist_completed:
                        st.info("Please review the setup checklist before continuing.")
                        st.session_state['page'] = 6  # Setup checklist page
                        st.rerun()
                    elif not progress['pre_study_completed']:
                        # Pre-study not completed, start from beginning (skip developer experience)
                        print("DEBUG: Pre-study not completed, starting from beginning")
                        st.session_state['page'] = 3  # AI tools page (page 3) - skip developer experience
                        st.rerun()
                    elif progress['issue_assigned']:
                        # Pre-study completed and issue assigned
                        # Check if all required issues are completed by getting next issue
                        print(f"DEBUG: Checking completion status for {REQUIRED_ISSUE_COUNT} required issue(s)")
                        from survey_data import get_next_issue_in_sequence
                        next_issue_result = get_next_issue_in_sequence(participant_id)

                        if next_issue_result['success'] and next_issue_result['issue'] is None:
                            # All issues are marked completed, but ensure post-PR surveys are done
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

                                # Route to the correct post-PR page
                                if nasa_tlx_1 is None:
                                    print(f"DEBUG: Issue {issue_id} NASA-TLX not done, redirecting to page 12")
                                    st.session_state['page'] = 12  # post_issue_questions_page
                                elif using_ai and ai_code_quality is None:
                                    print(f"DEBUG: Issue {issue_id} AI reflection not done, redirecting to page 13")
                                    st.session_state['page'] = 13  # post_issue_reflection_page
                                else:
                                    print(f"DEBUG: Issue {issue_id} survey done except reflection, redirecting to page 13")
                                    st.session_state['page'] = 13  # post_issue_reflection_page
                                st.rerun()

                            # All required issues completed, check if there are reviewed PRs needing updates
                            print("DEBUG: All required issues completed, checking for reviewed PRs")

                            # Check if there are any reviewed PRs that need updating
                            from survey_data import get_supabase_client
                            supabase_client = get_supabase_client()

                            try:
                                # Check total assigned issues
                                assigned_result = supabase_client.table('repo-issues')\
                                    .select('issue_id')\
                                    .eq('participant_id', participant_id)\
                                    .execute()
                                total_assigned = len(assigned_result.data) if assigned_result.data else 0

                                # Check for merged/closed PRs
                                reviewed_result = supabase_client.table('repo-issues')\
                                    .select('issue_id')\
                                    .eq('participant_id', participant_id)\
                                    .or_('is_merged.eq.true,is_closed.eq.true')\
                                    .execute()

                                # Check for completed PR surveys (learn_4 is not null)
                                pr_closed_result = supabase_client.table('pr-closed')\
                                    .select('issue_id, learn_4')\
                                    .eq('participant_id', participant_id)\
                                    .not_.is_('learn_4', 'null')\
                                    .execute()

                                reviewed_issue_ids = {item['issue_id'] for item in reviewed_result.data} if reviewed_result.data else set()
                                completed_survey_ids = {int(item['issue_id']) for item in pr_closed_result.data} if pr_closed_result.data else set()

                                # Check if there are reviewed PRs that haven't had surveys completed
                                has_pending_pr_surveys = len(reviewed_issue_ids - completed_survey_ids) > 0
                                total_reviewed_prs = len(reviewed_issue_ids)
                                # All PRs complete only if ALL assigned issues are merged/closed AND all surveys done
                                all_prs_closed = total_assigned > 0 and total_reviewed_prs >= total_assigned
                                all_pr_surveys_complete = all_prs_closed and len(completed_survey_ids) >= total_reviewed_prs

                                print(f"DEBUG: Total assigned: {total_assigned}, Reviewed PRs: {reviewed_issue_ids}, Completed surveys: {completed_survey_ids}")
                                print(f"DEBUG: Total reviewed PRs: {total_reviewed_prs}, All PRs closed: {all_prs_closed}, All surveys complete: {all_pr_surveys_complete}")

                                if has_pending_pr_surveys:
                                    # Has reviewed PRs needing updates, route to update page
                                    print("DEBUG: Has reviewed PRs needing updates, routing to update page")
                                    st.session_state['page'] = 18  # Update issue page
                                    st.rerun()
                                elif all_pr_surveys_complete:
                                    # All PRs are closed and all pr_closed surveys are filled
                                    # Check if post-study survey is already complete
                                    print("DEBUG: All PRs closed and all pr_closed surveys complete, checking post-study status")
                                    try:
                                        post_study_result = supabase_client.table('post-study')\
                                            .select('participant_id, ai_responsibility, value_reading_issue')\
                                            .eq('participant_id', participant_id)\
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
                                    except Exception as e:
                                        print(f"Error checking post-study status: {e}")
                                        # On error, route to end of study survey
                                        st.session_state['page'] = 25
                                        st.rerun()
                                else:
                                    # All surveys complete or no reviewed PRs yet, check post-exp1 completion
                                    print("DEBUG: All surveys complete or no reviewed PRs, checking post-exp1 status")
                                    try:
                                        post_exp1_result = supabase_client.table('post-exp1')\
                                            .select('workflow_comparison, ai_helpful_tasks, ai_wish_different, ai_suggestion_decisions')\
                                            .eq('participant_id', participant_id)\
                                            .execute()

                                        if post_exp1_result.data and len(post_exp1_result.data) > 0:
                                            post_exp1_data = post_exp1_result.data[0]
                                            workflow_comparison = post_exp1_data.get('workflow_comparison')
                                            ai_helpful_tasks = post_exp1_data.get('ai_helpful_tasks')
                                            ai_wish_different = post_exp1_data.get('ai_wish_different')
                                            ai_suggestion_decisions = post_exp1_data.get('ai_suggestion_decisions')

                                            # Check if workflow_comparison is missing -> route to page 14
                                            if not workflow_comparison or not str(workflow_comparison).strip():
                                                print("DEBUG: Post-exp1 workflow_comparison missing, routing to page 14")
                                                st.session_state['page'] = 14  # study_val_page
                                                st.rerun()
                                            # Check if any AI usage fields are missing -> route to page 15
                                            elif (not ai_helpful_tasks or not str(ai_helpful_tasks).strip() or
                                                  not ai_wish_different or not str(ai_wish_different).strip() or
                                                  not ai_suggestion_decisions or not str(ai_suggestion_decisions).strip()):
                                                print("DEBUG: Post-exp1 AI usage fields missing, routing to page 15")
                                                st.session_state['page'] = 15  # ai_usage_page
                                                st.rerun()
                                            else:
                                                # All post-exp1 complete, go to thank you page
                                                print("DEBUG: Post-exp1 complete, routing to thank you page")
                                                st.session_state['page'] = 17  # Thank you page
                                                st.rerun()
                                        else:
                                            # No post-exp1 record, route to page 14
                                            print("DEBUG: No post-exp1 record, routing to page 14")
                                            st.session_state['page'] = 14  # study_val_page
                                            st.rerun()
                                    except Exception as e:
                                        print(f"Error checking post-exp1 status: {e}")
                                        # On error, default to thank you page
                                        st.session_state['page'] = 17
                                        st.rerun()
                            except Exception as e:
                                print(f"Error checking for reviewed PRs: {e}")
                                # On error, default to thank you page
                                st.session_state['page'] = 17
                                st.rerun()
                        elif next_issue_result['success'] and next_issue_result['issue']:
                            # Has incomplete issues
                            next_issue = next_issue_result['issue']
                            has_time_estimate = next_issue.get('participant_estimate') is not None
                            is_completed = next_issue.get('is_completed', False)
                            checklist_completed_issue = next_issue.get('checklist_completed', False)

                            # Load next issue into session state
                            st.session_state['survey_responses'].update({
                                'assigned_issue': next_issue,
                                'issue_url': next_issue.get('issue_url'),
                                'issue_id': next_issue.get('issue_id'),
                                'current_issue_using_ai': next_issue.get('using_ai', False)
                            })

                            if is_completed and not checklist_completed_issue:
                                # Issue completed but survey not done, go to post-issue questions
                                print("DEBUG: Issue completed, survey pending, routing to post-issue questions")
                                st.session_state['page'] = 12  # post_issue_questions_page
                                st.rerun()
                            elif has_time_estimate and not is_completed:
                                # Has accepted issue and estimated time, route to issue completion page
                                print("DEBUG: Issue accepted with estimate, routing to issue completion page")
                                st.session_state['page'] = 10  # Issue completion page
                                st.rerun()
                            else:
                                # No time estimate yet or other state, go to issue assignment page
                                print("DEBUG: Routing to issue assignment page")
                                st.session_state['page'] = 8  # Issue assignment page
                                st.rerun()
                        else:
                            # Error or no issues, go to issue assignment page
                            print("DEBUG: Error or no issues, routing to issue assignment")
                            st.session_state['page'] = 8  # Issue assignment page
                            st.rerun()
                    else:
                        # Pre-study completed but no issue assigned, go to issue assignment page
                        st.info("Welcome back! You've already completed the pre-study survey.")
                        print("DEBUG: Routing to issue assignment page (no issue assigned yet)")
                        st.session_state['page'] = 8  # Issue assignment page
                        st.rerun()
                else:
                    # Couldn't check progress, just proceed normally (skip developer experience)
                    st.session_state['page'] = 3  # AI tools page (page 3) - skip developer experience
                    st.rerun()
            else:
                # ID is not valid, show error
                st.error(f"{validation_result['error']}")
