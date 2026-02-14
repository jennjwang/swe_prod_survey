"""
AI Responsibility question page shown after completing all PR closed surveys.
"""

import streamlit as st
from survey_components import page_header, navigation_buttons
from survey_utils import record_audio
from survey_data import get_supabase_client


def end_of_study_thank_you_page():
    """Display AI responsibility question."""
    page_header(
        "Final Reflections",
        "Thanks again for merging or closing all your PRs! Before we wrap up, we have a few final questions about your overall experience."
    )

    # Get participant ID
    participant_id = st.session_state['survey_responses'].get('participant_id', '')

    # ========== QUESTION 1: AI Responsibility ==========
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1.5rem;'>
        Did using AI change how responsible you felt for the final code? If errors were found in the PR, how would you attribute responsibility between yourself and the AI?
        </p>
        """, unsafe_allow_html=True)

    # Load previous response if exists
    previous_ai_response = st.session_state.get('ai_responsibility_response', '')

    # Create tabs for audio and text input
    tab1, tab2 = st.tabs(["🎤 Record Audio", "⌨️ Type Response"])

    with tab1:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Click the microphone button below to record your response. Your audio will be transcribed automatically.
            </p>
            """, unsafe_allow_html=True)
        transcript = record_audio("ai_responsibility", min_duration=10, max_duration=600)

    with tab2:
        st.markdown("""
            <p style='font-size:14px; margin-bottom: 0.5rem; color: #666;'>
            Type your response in the text box below.
            </p>
            """, unsafe_allow_html=True)
        text_response = st.text_area(
            "Your response:",
            key="ai_responsibility_text",
            value=previous_ai_response,
            height=200,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

    # Use whichever response is available
    if transcript:
        ai_responsibility_response = transcript
    elif text_response and text_response.strip():
        ai_responsibility_response = text_response
    else:
        ai_responsibility_response = previous_ai_response

    # Validation function
    def validate():
        # Check AI responsibility response
        if not ai_responsibility_response or not ai_responsibility_response.strip():
            st.warning('⚠️ Please provide a response to the AI responsibility question.')
            return False
        return True

    # Navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['ai_responsibility_response'] = ai_responsibility_response
        st.session_state['page'] = 18  # Back to update issue page
        st.rerun()

    def handle_submit():
        if not validate():
            return

        # Save to session state
        st.session_state['ai_responsibility_response'] = ai_responsibility_response

        # Save to database
        supabase_client = get_supabase_client()
        if supabase_client and participant_id:
            try:
                # Build database data object
                db_data = {
                    'participant_id': participant_id,
                    'ai_responsibility': ai_responsibility_response
                }

                # Check if record exists
                existing = supabase_client.table('post-study')\
                    .select('participant_id')\
                    .ilike('participant_id', participant_id)\
                    .execute()

                if existing.data and len(existing.data) > 0:
                    # Update existing record
                    result = supabase_client.table('post-study')\
                        .update(db_data)\
                        .ilike('participant_id', participant_id)\
                        .execute()
                else:
                    # Insert new record
                    result = supabase_client.table('post-study')\
                        .insert(db_data)\
                        .execute()

                if result.data:
                    st.success("Your response has been saved!")
                    print(f"AI responsibility response saved for participant {participant_id}")
                else:
                    st.error("⚠️ Error saving response. Please try again.")
                    return

            except Exception as e:
                st.error(f"⚠️ Error saving response: {e}")
                print(f"Error saving AI responsibility response: {e}")
                return

        # Navigate to code activities value page
        st.session_state['page'] = 24  # Code activities value page
        st.rerun()

    # Navigation buttons
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_submit,
        back_key="end_study_back",
        next_key="end_study_submit",
        next_label="Next",
        validation_fn=validate,
        validation_error=""
    )
