"""
Centralized CSS styles for the developer survey application.
Uses sustainable styling approaches that won't break with Streamlit updates.

APPROACH:
- Use stable selectors (data attributes, ARIA roles)
- Use broad selectors for consistent styling
- Avoid emotion-cache classes that change
- Focus on semantic HTML elements
"""

SURVEY_STYLES = """
<style>
/* ========================================
   LAYOUT & SPACING
   ======================================== */

.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    padding-left: 5rem;
    padding-right: 5rem;
    max-width: 900px;
}

h1, h2, h3 {
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
}

p {
    margin-bottom: 1.5rem;
    line-height: 1.8;
    font-size: 18px;
}

hr {
    margin-top: 2.5rem;
    margin-bottom: 2.5rem;
}

/* ========================================
   BUTTONS
   ======================================== */

.stButton > button {
    font-size: 18px;
    padding: 8px 30px;
}

/* ========================================
   FORM ELEMENTS - Broad, Sustainable Styling
   ======================================== */

/* All form containers */
.stSelectbox, .stTextArea, .stRadio, .stSlider {
    margin-bottom: 0.25rem !important; /* tighter stacking between items */
}

/* Labels: match body font and tighten spacing */
label, .stMarkdown label {
    font-size: 18px !important; /* align with body */
    font-weight: 500 !important;
    color: inherit !important;
    margin-bottom: 0rem !important; /* minimal gap above slider */
}

/* ========================================
   SLIDER - Sustainable Styling
   Uses data-baseweb and role attributes which are stable
   ======================================== */

/* Slider container */
.stSlider {
    max-width: 80%;
    margin-left: 0.5rem;
    margin-top: 0rem !important;
    margin-bottom: 0rem !important; /* even tighter stacking */
}

/* Slider thumb using stable ARIA role */
[role="slider"] {
    width: 15px !important;
    height: 15px !important;
    background-color: #ff4b4b !important;
    /* border: 3px solid #cc3c3c !important; */
}

/* Alternative: target ALL divs in slider for max coverage */
.stSlider [data-baseweb="slider"] { margin-top: 0rem !important; margin-bottom: 0rem !important; }
.stSlider [data-baseweb="slider"] div { font-size: 16px; color: inherit;}
.stSlider span{
    color: gray !important;

.stElementContainer {
    margin-bottom: 0rem;
}

</style>
"""


# Alternative: Inline styling function for critical elements
def get_question_style():
    """
    Returns inline style dict for questions.
    More sustainable than CSS for frequently changing elements.
    """
    return {
        'font-size': '20px',
        'font-weight': '600',
        'color': '#2c3e50',
        'margin-bottom': '1rem'
    }


def get_slider_container_style():
    """
    Returns inline style for slider containers.
    """
    return {
        'margin-bottom': '1.5rem'
    }
