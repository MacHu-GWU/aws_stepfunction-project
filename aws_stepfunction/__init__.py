# -*- coding: utf-8 -*-

"""
Package Description.
"""

from ._version import __version__

__short_description__ = "Package short description."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------
try:
    from .state_machine import StateMachine
    from .state import (
        State,
        Task, Parallel, Map, Pass, Wait, Choice, Succeed, Fail,
        Retry, Catch,
    )
    from .choice_rule import (
        ChoiceRule,
        and_, or_, not_,
        Var,
    )
    from . import actions
    from .step_function import StepFunctionObject
    from .constant import Constant
except ImportError as e:
    print(e)
