# -*- coding: utf-8 -*-

import typing as T

if T.TYPE_CHECKING:
    from .state_machine import StateMachine
    from .state import State


class ValidationError(Exception):
    pass


class ExecutionError(Exception):
    pass


class StateMachineError(Exception):
    @classmethod
    def make(cls, sm: 'StateMachine', msg: str):
        return cls(
            f"StateMachine(id={sm.id}): {msg}"
        )


class StateError(Exception):
    pass


class StateMachineValidationError(
    StateMachineError,
    ValidationError,
):
    pass


class StateMachineExecutionError(
    StateMachineError,
    ExecutionError,
):
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
