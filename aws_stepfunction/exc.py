# -*- coding: utf-8 -*-

"""

"""

import typing as T

if T.TYPE_CHECKING:
    from .workflow import Workflow
    from .state import State


class ValidationError(Exception):
    pass


class ExecutionError(Exception):
    pass


class StateError(Exception):
    """
    Raise when an error is related to a state.
    """
    pass


class StateValidationError(
    StateError,
    ValidationError,
):
    @classmethod
    def make(cls, state: 'State', msg: str):
        return cls(
            f"State(id={state.id}): {msg}"
        )


class WorkflowError(Exception):
    """
    Raise when an error is related to a workflow.
    """

    @classmethod
    def make(cls, wf: 'Workflow', msg: str):
        return cls(
            f"Workflow(id={wf.id}): {msg}"
        )


class WorkflowValidationError(
    WorkflowError,
    ValidationError,
):
    pass


class WorkflowExecutionError(
    WorkflowError,
    ExecutionError,
):
    pass
