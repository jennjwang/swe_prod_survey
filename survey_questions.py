"""
Survey questions and configuration data.
"""

# Professional experience options
EXPERIENCE_OPTIONS = (
    "Less than 1 year",
    "1–3 years",
    "4–6 years",
    "7–10 years",
    "More than 10 years"
)


# AI tool usage questions
AI_EXPERIENCE_QUESTIONS = {
    'llm_hours': 'Approximately how many hours have you spent using <strong>AI assistants</strong> such as ChatGPT, Claude, or Gemini?',
    'agent_hours': 'Approximately how many hours have you spent using <strong>AI coding agents</strong> such as GitHub Copilot, Cursor, or Claude Code?',
}

AI_HOURS_OPTIONS = [
    "Not selected",
    "0 hours",
    "1–10 hours",
    "10–100 hours",
    "100–1000 hours",
    ">1000 hours"
]

# Code experience options
CODE_EXPERIENCE_OPTIONS = [
    "Fewer than 100",
    "100–1,000",
    "1,001–10,000",
    "10,001–50,000",
    "More than 50,000"
]
