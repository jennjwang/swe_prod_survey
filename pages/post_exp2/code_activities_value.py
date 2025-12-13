"""
Code Activities Value page for rating the value of different development activities.
"""

import streamlit as st
from survey_components import page_header, navigation_buttons
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

# Code activities organized by category (full descriptions)
CODE_ACTIVITIES = {
    "Understanding the Task": {
        "reading_issue": "Reading the assigned issue",
        "reading_docs": "Reading documentation",
        "reading_code": "Reading code"
    },
    "Implementation Work": {
        "writing_code": "Writing code",
        "writing_tests": "Writing tests",
        "writing_docs": "Writing documentation",
        "refactoring": "Refactoring code"
    },
    "Verification & Quality": {
        "running_tests": "Running automated tests",
        "manual_testing": "Manual testing",
        "linting_formatting": "Linting/formatting",
        "troubleshooting": "Debugging"
    },
    "PR Workflow & Collaboration": {
        "git_operations": "Git operations",
        "creating_pr": "Creating PR",
        "reading_review_comments": "Reading review comments",
        "responding_to_review": "Responding to review"
    },
    "Environment / Tooling": {
        "setup": "Environment setup",
        # "building_compiling": "Building/compiling"
    }
}


def code_activities_value_page():
    """Display code activities value rating page."""
    page_header(
        "Code Activities",
        "Consider each activity and rate whether it reflects high-value work for you. "
    )

    # Definition box
    st.markdown("""
        <div style='background-color: #f0f0f0; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem;'>
        <p style='margin: 0; font-size: 15px;'>
        <strong>"High-value work"</strong> refers to tasks you consider are worth your time—those that feel meaningful, important, or impactful compared with routine or overhead work.
        </p>
        </div>
    """, unsafe_allow_html=True)


    # Get participant ID
    participant_id = st.session_state['survey_responses'].get('participant_id', '')

    # Load previous responses
    previous_responses = st.session_state.get('code_activities_value', {})

    # Collect ratings for all activities
    all_ratings = {}

    for category, activities in CODE_ACTIVITIES.items():
        # Category header
        st.markdown(f"""
            <p style='font-size:16px; font-weight:600; margin-top: 1.2rem; margin-bottom: 0.8rem;
                       color: #1f77b4;'>
            {category}
            </p>
            """, unsafe_allow_html=True)

        # Activities within category - horizontal layout with columns
        for key, description in activities.items():
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(f"""
                    <p style='font-size:15px; font-weight:400; margin: 0; padding-top: 1.5rem;'>
                    {description}
                    </p>
                    """, unsafe_allow_html=True)

            with col2:
                # Get previous value, default to "Not selected"
                prev_value = previous_responses.get(key, "Not selected")
                if isinstance(prev_value, int):
                    # Convert numeric value to string option
                    if prev_value == 0:
                        prev_value = "Not selected"
                    else:
                        # Find matching option (e.g., 1 -> "1 - Not at all valuable")
                        for option in VALUE_RATING_OPTIONS:
                            if option.startswith(str(prev_value)):
                                prev_value = option
                                break
                        else:
                            prev_value = "Not selected"
                elif prev_value is None:
                    prev_value = "Not selected"

                rating = st.select_slider(
                    label="",
                    options=VALUE_RATING_OPTIONS,
                    value=prev_value,
                    key=f"value_{key}"
                )
                all_ratings[key] = rating

    # Validation function
    def validate():
        # Check code activities ratings
        unanswered = []
        for key, value in all_ratings.items():
            if value == "Not selected" or value == 0:
                # Find the activity description for better error message
                for category, activities in CODE_ACTIVITIES.items():
                    if key in activities:
                        unanswered.append(activities[key])
                        break

        if unanswered:
            st.warning(f'⚠️ Please rate all activities. Missing: {", ".join(unanswered)}')
            return False
        return True

    # Navigation handlers
    def handle_back():
        # Save to session state
        st.session_state['code_activities_value'] = all_ratings
        st.session_state['page'] = 25  # Back to end of study thank you page (AI responsibility)
        st.rerun()

    def handle_submit():
        if not validate():
            return

        # Save to session state
        st.session_state['code_activities_value'] = all_ratings

        # Save to database
        supabase_client = get_supabase_client()
        if supabase_client and participant_id:
            try:
                # Build database data object with code activities ratings as numeric values
                db_data = {}
                for key, value in all_ratings.items():
                    if value and value != "Not selected" and value != 0:
                        # Convert string option to numeric value (e.g., "1 - Not at all valuable" -> 1)
                        if isinstance(value, str):
                            numeric_value = int(value.split()[0])
                            db_data[f'value_{key}'] = numeric_value
                        else:
                            db_data[f'value_{key}'] = value

                # Check if record exists
                existing = supabase_client.table('post-study')\
                    .select('participant_id')\
                    .eq('participant_id', participant_id)\
                    .execute()

                if existing.data and len(existing.data) > 0:
                    # Update existing record (preserve ai_responsibility if it exists)
                    # First get existing data
                    existing_data = supabase_client.table('post-study')\
                        .select('*')\
                        .eq('participant_id', participant_id)\
                        .execute()
                    
                    if existing_data.data and len(existing_data.data) > 0:
                        # Merge with existing data
                        existing_record = existing_data.data[0]
                        db_data = {**existing_record, **db_data}
                    
                    result = supabase_client.table('post-study')\
                        .update(db_data)\
                        .eq('participant_id', participant_id)\
                        .execute()
                else:
                    # Insert new record (shouldn't happen if AI responsibility was saved first)
                    result = supabase_client.table('post-study')\
                        .insert({
                            'participant_id': participant_id,
                            **db_data
                        })\
                        .execute()

                if result.data:
                    st.success("Your responses have been saved!")
                    print(f"Code activities value responses saved for participant {participant_id}")
                else:
                    st.error("⚠️ Error saving responses. Please try again.")
                    return

            except Exception as e:
                st.error(f"⚠️ Error saving responses: {e}")
                print(f"Error saving code activities value responses: {e}")
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
        back_key="code_activities_back",
        next_key="code_activities_submit",
        next_label="Submit",
        validation_fn=validate,
        validation_error=""
    )

