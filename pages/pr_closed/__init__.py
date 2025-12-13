"""
PR closed survey pages.
"""

from .update_issue import update_issue_page
from .collaboration_questions import collaboration_questions_page
from .engagement_questions import engagement_questions_page
from .learning_outcomes_questions import learning_outcomes_questions_page
from .pr_closed_thank_you import pr_closed_thank_you_page

__all__ = [
    'update_issue_page',
    'collaboration_questions_page',
    'engagement_questions_page',
    'learning_outcomes_questions_page',
    'pr_closed_thank_you_page',
]
