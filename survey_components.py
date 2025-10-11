"""
Reusable UI components for the survey.
"""

import streamlit as st


def page_header(title: str, description: str):
    """Display a consistent page header."""
    st.header(title)
    st.markdown(f"""
        <p style='font-size:18px; font-weight: 600; margin-bottom: 2rem'>
        {description}
        </p>
        """, unsafe_allow_html=True)


def question_label(text: str, font_size: int = 18, font_weight: int = 400):
    """Display a consistent question label."""
    st.markdown(
        f"<p style='font-size:{font_size}px; font-weight:{font_weight}; margin-bottom:0.5rem;'>{text}</p>", 
        unsafe_allow_html=True
    )


def navigation_buttons(
    on_back=None, 
    on_next=None, 
    back_key="back", 
    next_key="next",
    next_label="Next",
    validation_fn=None,
    validation_error="Please fill out all fields before proceeding."
):
    """
    Display back and next navigation buttons with optional validation.
    
    Args:
        on_back: Callback function for back button
        on_next: Callback function for next button
        back_key: Unique key for back button
        next_key: Unique key for next button
        next_label: Label for next button (default: "Next")
        validation_fn: Function that returns True if validation passes
        validation_error: Error message to show if validation fails
    """
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        back_clicked = st.button("Back", key=back_key)
    with col3:
        next_clicked = st.button(next_label, key=next_key)
    
    if back_clicked and on_back:
        on_back()
    elif next_clicked and on_next:
        if validation_fn is None or validation_fn():
            on_next()
        else:
            st.error(validation_error)


def slider_question(
    question_text: str,
    options: list,
    key: str,
    previous_value=None,
    font_size: int = 18,
    font_weight: int = 400
):
    """Display a slider question with consistent styling."""
    st.markdown(
        f"<p style='font-size:{font_size}px; margin-bottom:0rem; font-weight:{font_weight};'>{question_text}</p>", 
        unsafe_allow_html=True
    )
    
    default_value = previous_value if previous_value else options[0]
    return st.select_slider(
        label="",
        options=options,
        value=default_value,
        key=key
    )


def selectbox_question(
    question_text: str,
    options: list,
    key: str,
    previous_value=None,
    font_size: int = 18,
    font_weight: int = 400,
    placeholder: str = None
):
    """Display a selectbox question with consistent styling."""
    question_label(question_text, font_size, font_weight)
    
    default_index = None
    if previous_value and previous_value in options:
        default_index = options.index(previous_value)
    
    return st.selectbox(
        label="",
        options=options,
        index=default_index,
        key=key,
        placeholder=placeholder
    )


def text_area_question(
    question_text: str,
    key: str,
    previous_value: str = "",
    height: int = 100,
    placeholder: str = "",
    font_size: int = 18,
    font_weight: int = 400
):
    """Display a text area question with consistent styling."""
    question_label(question_text, font_size, font_weight)
    
    return st.text_area(
        label="",
        value=previous_value,
        key=key,
        height=height,
        placeholder=placeholder
    )


def text_input_question(
    question_text: str,
    key: str,
    previous_value: str = "",
    placeholder: str = "",
    font_size: int = 18,
    font_weight: int = 400
):
    """Display a text input question with consistent styling."""
    question_label(question_text, font_size, font_weight)
    
    return st.text_input(
        label="",
        value=previous_value,
        key=key,
        placeholder=placeholder
    )

