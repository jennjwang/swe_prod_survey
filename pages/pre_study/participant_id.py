"""
Participant ID page for the survey.
"""

import streamlit as st
from survey_components import page_header, text_input_question
from survey_utils import save_and_navigate, next_page
from survey_data import validate_participant_id, get_participant_progress, get_repository_assignment


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
                    print(f"DEBUG: pre_study_completed = {progress['pre_study_completed']}")
                    print(f"DEBUG: issue_assigned = {progress['issue_assigned']}")
                    print(f"DEBUG: issue_completed = {progress['issue_completed']}")
                    
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
                        # Check if all 4 issues are completed by getting next issue
                        from survey_data import get_next_issue_in_sequence
                        next_issue_result = get_next_issue_in_sequence(participant_id)

                        if next_issue_result['success'] and next_issue_result['issue'] is None:
                            # All 4 issues completed, go to final completion
                            print("DEBUG: All 4 issues completed, routing to final completion")
                            st.session_state['page'] = 17  # Thank you page (all issues complete)
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
                                st.session_state['page'] = 11  # AI condition questions page
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
                        st.info("✅ Welcome back! You've already completed the pre-study survey.")
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
