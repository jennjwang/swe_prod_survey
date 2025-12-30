"""
Post-PR survey pages package.
Contains pages that participants complete after submitting their PR.
"""

from .post_issue_questions import post_issue_questions_page
from .post_issue_reflection import post_issue_reflection_page
from .completion import completion_page

__all__ = [
    'post_issue_questions_page',
    'post_issue_reflection_page',
    'completion_page'
]
