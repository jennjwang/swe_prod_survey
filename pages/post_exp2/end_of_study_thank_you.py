"""
Final thank you page shown after completing all end of study questions.
"""

import streamlit as st
from survey_components import page_header, slider_question, navigation_buttons
from survey_utils import record_audio
from survey_data import get_supabase_client


# Value rating scale
VALUE_RATING_OPTIONS = [
    "Not selected",
    "1 - Not at all valuable",
    "2 - Slightly valuable",
    "3 - Moderately valuable",
    "4 - Very valuable",
    "5 - Extremely valuable"
]

# Code activities organized by category
CODE_ACTIVITIES = {
    "Understanding the Task": {
        "reading_issue": "reading issue — reviewing the problem description, feature request, or bug report",
        "reading_docs": "reading docs — consulting external documentation, API references, or project guides",
        "reading_code": "reading code — exploring existing codebase to understand context and architecture"
    },
    "Implementation Work": {
        "writing_code": "writing code — editing or adding code related to the PR",
        "writing_tests": "writing tests — adding or updating automated tests",
        "writing_docs": "writing docs — updating documentation or notes required for the PR",
        "refactoring": "refactoring — improving code structure without changing behavior"
    },
    "Verification & Quality": {
        "running_tests": "running tests — executing automated test suites",
        "manual_testing": "manual testing — manually verifying the feature or fix works",
        "linting_formatting": "linting/formatting — running and fixing code style checks",
        "troubleshooting": "troubleshooting — debugging failures, analyzing error messages or logs"
    },
    "PR Workflow & Collaboration": {
        "git_operations": "git operations — branching, staging, committing, pushing changes",
        "creating_pr": "creating PR — writing PR title, description, and filling out templates",
        "reading_review_comments": "reading review comments — processing feedback from maintainers/reviewers",
        "responding_to_review": "responding to review — replying to questions, explaining decisions"
    },
    "Environment / Tooling": {
        "setup": "setup — opening the IDE, loading the project, configuring tools at session start",
        "building_compiling": "building/compiling — waiting for the project to build or compile"
    }
}


def end_of_study_thank_you_page():
    """Display end of study questions including AI responsibility and code activities value."""
    page_header(
        "End of Study Questions",
        "Now that you've completed feedback on all your PRs, we have a few final questions."
    )

    # Get participant ID
    participant_id = st.session_state['survey_responses'].get('participant_id', '')

    # ========== QUESTION 1: AI Responsibility ==========
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1.5rem;'>
        1. Did using AI change how responsible you felt for the final code?
        If errors were found in the PR, how would you attribute responsibility between yourself and the AI?
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

    st.divider()
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    # ========== QUESTION 2: Code Activities Value ==========
    st.markdown("""
        <p style='font-size:18px; font-weight:600; margin-bottom: 1rem;'>
        2. Code Activities Survey
        </p>
        <p style='font-size:16px; font-weight:400; margin-bottom: 1.5rem;'>
        We'd like to understand what work you find most valuable in open source development.
        </p>
        """, unsafe_allow_html=True)

    # Definition box
    st.markdown("""
        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;'>
            <p style='font-size:16px; font-weight:600; margin-bottom: 0.5rem;'>
            Definition: High-value work
            </p>
            <p style='font-size:15px; margin-bottom: 0;'>
            "High-value work" means work you personally feel is worth your time — important,
            impactful, or otherwise worthwhile compared to other tasks (not just repetitive overhead).
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <p style='font-size:17px; font-weight:500; margin-bottom: 1.5rem;'>
        For each task below, rate how valuable each activity is to you in open source development.
        </p>
        """, unsafe_allow_html=True)

    # Load previous responses
    previous_responses = st.session_state.get('code_activities_value', {})

    # Collect ratings for all activities
    all_ratings = {}

    for category, activities in CODE_ACTIVITIES.items():
        # Category header
        st.markdown(f"""
            <p style='font-size:18px; font-weight:600; margin-top: 1.5rem; margin-bottom: 1rem;
                       color: #1f77b4;'>
            {category}
            </p>
            """, unsafe_allow_html=True)

        # Activities within category
        for key, description in activities.items():
            all_ratings[key] = slider_question(
                description,
                VALUE_RATING_OPTIONS,
                f"value_{key}",
                previous_responses.get(key, "Not selected"),
                font_size=16,
                font_weight=400
            )
            st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

    # Validation function
    def validate():
        # Check AI responsibility response
        if not ai_responsibility_response or not ai_responsibility_response.strip():
            st.warning('⚠️ Please provide a response to the AI responsibility question.')
            return False

        # Check code activities ratings
        unanswered = []
        for key, value in all_ratings.items():
            if value == "Not selected":
                # Find the activity description for better error message
                for category, activities in CODE_ACTIVITIES.items():
                    if key in activities:
                        unanswered.append(key.replace('_', ' '))
                        break

        if unanswered:
            st.warning(f'⚠️ Please rate all activities. Missing: {", ".join(unanswered)}')
            return False
        return True

    # Navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['ai_responsibility_response'] = ai_responsibility_response
        st.session_state['code_activities_value'] = all_ratings
        st.session_state['page'] = 18  # Back to update issue page
        st.rerun()

    def handle_submit():
        if not validate():
            return

        # Save to session state
        st.session_state['ai_responsibility_response'] = ai_responsibility_response
        st.session_state['code_activities_value'] = all_ratings

        # Save to database
        supabase_client = get_supabase_client()
        if supabase_client and participant_id:
            try:
                # Build database data object
                db_data = {
                    'participant_id': participant_id,
                    'ai_responsibility': ai_responsibility_response
                }

                # Add code activities ratings as numeric values
                for key, value in all_ratings.items():
                    if value and value != "Not selected":
                        db_data[f'value_{key}'] = int(value.split()[0])

                # Check if record exists
                existing = supabase_client.table('post-study')\
                    .select('participant_id')\
                    .eq('participant_id', participant_id)\
                    .execute()

                if existing.data and len(existing.data) > 0:
                    # Update existing record
                    result = supabase_client.table('post-study')\
                        .update(db_data)\
                        .eq('participant_id', participant_id)\
                        .execute()
                else:
                    # Insert new record
                    result = supabase_client.table('post-study')\
                        .insert(db_data)\
                        .execute()

                if result.data:
                    st.success("✅ Your responses have been saved!")
                    print(f"End of study responses saved for participant {participant_id}")
                else:
                    st.error("⚠️ Error saving responses. Please try again.")
                    return

            except Exception as e:
                st.error(f"⚠️ Error saving responses: {e}")
                print(f"Error saving end of study responses: {e}")
                return

        # Clear pr_closed session state
        st.session_state.pop('pr_closed_selected_issue', None)

        # Navigate to final thank you page
        st.session_state['page'] = 26  # Final thank you page
        st.rerun()

    # Navigation buttons
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    navigation_buttons(
        on_back=handle_back,
        on_next=handle_submit,
        back_key="end_study_back",
        next_key="end_study_submit",
        next_label="Submit",
        validation_fn=validate,
        validation_error=""
    )
