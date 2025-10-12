"""
Post-PR survey pages package.
Contains all pages that participants complete after submitting their PR.
"""

from .ai_condition_questions import ai_condition_questions_page
from .post_issue_questions import post_issue_questions_page
from .completion import completion_page, already_completed_page

__all__ = [
    'ai_condition_questions_page',
    'post_issue_questions_page',
    'completion_page',
    'already_completed_page'
]
