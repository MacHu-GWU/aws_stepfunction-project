# -*- coding: utf-8 -*-

import typing as T

if T.TYPE_CHECKING:
    from .state_machine import StateMachine


class ValidationError(Exception):
    pass


class ExecutionError(Exception):
    pass


class StateMachineError(Exception):
    @classmethod
    def make(cls, sm: 'StateMachine', msg: str):
        return cls(
            f"StateMachine(ID={sm.ID}): {msg}"
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
    pass
