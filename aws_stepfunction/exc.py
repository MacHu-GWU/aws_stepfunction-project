# -*- coding: utf-8 -*-


class ValidationError(Exception):
    pass


class ExecutionError(Exception):
    pass


class StateMachineError(Exception):
    pass


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
