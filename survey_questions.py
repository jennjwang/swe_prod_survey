"""
Survey questions and configuration data.
"""

# Work satisfaction questions
SATISFACTION_QUESTIONS = {
    'abilities_use': 'The chance to do something that makes use of my abilities',
    'community_recognition': 'The chance to be "somebody" in the community',
    'work_alone': 'The chance to work alone on the job',
    'freedom_judgment': 'The freedom to use my own judgment',
    'own_methods': 'The chance to try my own methods of doing the work',
    'accomplishment': 'The feeling of accomplishment I get from my work',
    'learning': 'The opportunity to learn new skills from my work',
    'praise': 'The praise you get for doing a good job'
}

# Professional experience options
EXPERIENCE_OPTIONS = (
    "Less than 1 year",
    "1–3 years",
    "4–6 years",
    "7–10 years",
    "More than 10 years"
)

# Slider options for satisfaction ratings
SATISFACTION_SLIDER_OPTIONS = [
    "Not selected",
    "1: Very dissatisfied",
    "2: Dissatisfied",
    "3: Neutral",
    "4: Satisfied",
    "5: Very satisfied"
]

# Self-efficacy questions
SELF_EFFICACY_QUESTIONS = {
    'problem_solving': 'I can solve most problems if I invest the necessary effort',
    'find_solutions': 'If I am stuck on a problem, I can usually find one or more solutions',
    'handle_unexpected': 'I can usually handle whatever comes my way'
}

SELF_EFFICACY_OPTIONS = [
    "Not selected",
    "1: Not at all true",
    "2: Hardly true",
    "3: Moderately true",
    "4: Exactly true"
]

# AI tool usage questions
AI_FREQUENCY_QUESTIONS = {
    'debugging': 'How often do you use AI tools for debugging?',
    'code_generation': 'How often do you use AI tools for code generation?',
    'code_review': 'How often do you use AI tools for code review?',
    'documentation': 'How often do you use AI tools for writing documentation?',
    'learning': 'How often do you use AI tools for learning new concepts?'
}

FREQUENCY_OPTIONS = [
    "Not selected",
    "Never",
    "Rarely",
    "Sometimes",
    "Often",
    "Always"
]

# Task estimation questions
TASK_ESTIMATION_QUESTIONS = {
    'before_ai': 'How many hours per week did you spend on coding tasks BEFORE using AI tools?',
    'after_ai': 'How many hours per week do you spend on coding tasks AFTER using AI tools?',
    'quality_change': 'Has the quality of your work changed after using AI tools?'
}

QUALITY_CHANGE_OPTIONS = [
    "Not selected",
    "Significantly decreased",
    "Slightly decreased",
    "No change",
    "Slightly increased",
    "Significantly increased"
]

