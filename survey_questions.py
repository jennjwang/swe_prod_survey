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
    'comprehension': 'I can understand and navigate unfamiliar parts of the codebase.',
    'design': 'I can plan the steps needed to develop a program from its requirements.',
    'implementation': 'I can write code that solves a specified problem.',
    'debugging': 'I can identify and fix errors in a codebase.',
    'testing': 'I can write tests to verify the correctness of a program.',
    'cooperation': 'I can explain my design decisions clearly during code reviews.'
}

SELF_EFFICACY_OPTIONS = [
    "Not selected",
    "1: I am not confident at all",
    "2: I am slightly confident",
    "3: I am moderately confident",
    "4: I am very confident",
    "5: I am absolutely confident"
]

# AI tool usage questions
AI_EXPERIENCE_QUESTIONS = {
    'llm_hours': 'Approximately how many hours had you spent using <strong>AI assistants</strong> such as ChatGPT, Claude, or Copilot?',
    'cursor_hours': 'Approximately how many hours had you spent using <strong>Cursor</strong>?',
    'ai_agents_hours': 'Approximately how many hours had you spent using <strong>AI coding agents</strong> such as Claude Code or Codex?'
}

AI_HOURS_OPTIONS = [
    "Not selected",
    "0 hours",
    "1–10 hours",
    "10–100 hours",
    "100–1000 hours",
    ">1000 hours"
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

