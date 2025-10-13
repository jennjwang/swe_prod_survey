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
        "Please enter your Participant ID to begin the survey."
    )
    
    # Load previous participant ID if it exists
    previous_participant_id = st.session_state['survey_responses'].get('participant_id', '')
    
    # Participant ID input
    participant_id = text_input_question(
        "Participant ID:",
        "participant_id_input",
        previous_participant_id,
        placeholder="Enter your participant ID"
    )
    
    st.info("**Note:** Your Participant ID is case-sensitive. Please enter it exactly as provided.")
    
    # Navigation
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        back_clicked = st.button("Back", key="participant_id_back")
    with col3:
        next_clicked = st.button("Next", key="participant_id_next")
    
    if back_clicked:
        save_and_navigate('back', participant_id=participant_id)
    elif next_clicked:
        # Basic validation first
        if not participant_id or not participant_id.strip():
            st.error("Please enter your Participant ID to proceed.")
        else:
            # Validate against database
            with st.spinner('Validating Participant ID...'):
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
                        st.session_state['survey_responses'].update({
                            'professional_experience': pre_data.get('professional_experience'),
                            'occupation_description': pre_data.get('occupation_description'),
                            'assigned_repository': pre_data.get('assigned_repository'),
                            'repository_url': pre_data.get('repository_url'),
                            'forked_repository_url': pre_data.get('forked_repository_url'),
                            'code_experience': pre_data.get('code_experience'),
                            'self_efficacy': {
                                'comprehension': pre_data.get('self_efficacy_comprehension'),
                                'design': pre_data.get('self_efficacy_design'),
                                'implementation': pre_data.get('self_efficacy_implementation'),
                                'debugging': pre_data.get('self_efficacy_debugging'),
                                'testing': pre_data.get('self_efficacy_testing'),
                                'cooperation': pre_data.get('self_efficacy_cooperation'),
                            },
                            'satisfaction': {
                                'abilities_use': pre_data.get('satisfaction_abilities_use'),
                                'community_recognition': pre_data.get('satisfaction_community_recognition'),
                                'work_alone': pre_data.get('satisfaction_work_alone'),
                                'freedom_judgment': pre_data.get('satisfaction_freedom_judgment'),
                                'own_methods': pre_data.get('satisfaction_own_methods'),
                                'accomplishment': pre_data.get('satisfaction_accomplishment'),
                                'learning': pre_data.get('satisfaction_learning'),
                                'praise': pre_data.get('satisfaction_praise'),
                            },
                            'ai_experience': {
                                'llm_hours': pre_data.get('ai_experience_llm_hours'),
                                'cursor_hours': pre_data.get('ai_experience_cursor_hours'),
                                'ai_agents_hours': pre_data.get('ai_experience_ai_agents_hours'),
                            }
                        })
                        st.session_state['pre_study_saved'] = True
                    
                    # Load issue data if it exists
                    if progress['issue_assigned'] and progress['issue_data']:
                        issue_data = progress['issue_data']
                        st.session_state['survey_responses'].update({
                            'assigned_issue': issue_data,
                            'issue_url': issue_data.get('issue_url'),
                            'issue_id': issue_data.get('issue_id')
                        })
                    
                    # Debug output
                    print(f"DEBUG: Progress data: {progress}")
                    print(f"DEBUG: issue_assigned = {progress['issue_assigned']}")
                    print(f"DEBUG: issue_completed = {progress['issue_completed']}")
                    
                    # Route based on progress
                    if progress['issue_assigned']:
                        if progress['issue_completed']:
                            # Issue is completed, check if survey is also completed
                            if progress['survey_completed']:
                                # Both issue and survey completed, go to already completed page
                                print("DEBUG: Routing to already completed page (both issue and survey completed)")
                                st.session_state['page'] = 14  # Already completed page
                            else:
                                # Issue completed but survey not completed, go to AI condition questions
                                print("DEBUG: Routing to AI condition questions page (issue completed, survey not completed)")
                                st.session_state['page'] = 12  # AI condition questions page
                            st.rerun()  # Use st.rerun() instead of next_page() to avoid incrementing
                        else:
                            # Issue is assigned but not completed, go to issue completion page
                            print("DEBUG: Routing to issue completion page (issue not completed)")
                            st.session_state['page'] = 11  # Issue completion page
                            st.rerun()  # Use st.rerun() instead of next_page() to avoid incrementing
                    elif progress['pre_study_completed']:
                        # Skip to issue assignment
                        st.info("✅ Welcome back! You've already completed the pre-study survey.")
                        st.session_state['page'] = 8  # Pre-study complete page (will show saved message)
                        next_page()
                    else:
                        # Start from beginning
                        next_page()
                else:
                    # Couldn't check progress, just proceed normally
                    next_page()
            else:
                # ID is not valid, show error
                st.error(f"⚠️ {validation_result['error']}")

