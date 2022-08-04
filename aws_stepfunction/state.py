# -*- coding: utf-8 -*-

import typing as T

import attr

from . import exc
from .constant import (
    Constant as C,
    ErrorCodeEnum,
)
from .utils import short_uuid
from .model import StepFunctionObject
from .state_machine import _context, StateMachine


# ------------------------------------------------------------------------------
# State Data Model
# ------------------------------------------------------------------------------
@attr.s
class State(StepFunctionObject):
    ID: str = attr.ib(factory=lambda: short_uuid())
    Type: str = attr.ib(default=None)
    Comment: T.Optional[str] = attr.ib(default=None)

    def __attrs_post_init__(self):
        if len(_context.stack):
            sm = _context.stack[-1]
            sm.add_state(self)

    def _serialize(self) -> dict:
        data = self.to_dict()
        data.pop("ID")
        if data.get(C.ResultPath, None) == "null":
            data[C.ResultPath] = None
        return data


def _create_single_machine_from_state(state: '_HasNextOrEnd') -> 'StateMachine':
    """
    Tran
    """
    with StateMachine() as sm:
        sm._is_parallel_branch = True
        sm.add_state(state)
        sm.set_start_at(state)
        state.end()

    top_level_sm = _context.current
    if state.ID in top_level_sm.States:
        top_level_sm.States.pop(state.ID)

    return sm


@attr.s
class _HasNextOrEnd(State):
    Next: T.Optional[str] = attr.ib(default=None)
    End: T.Optional[bool] = attr.ib(default=None)

    def _check_next_and_end(self):
        if self.End is True:
            if self.Next:
                # when "End" is True, you can NOT have "Next"
                raise exc.StateValidationError
        else:
            if not self.Next:
                # when "End" is not True, you HAVE TO have "Next"
                raise exc.StateValidationError

    def _pre_serialize_validation(self):
        self._check_next_and_end()

    def next(self, state: 'State') -> T.Union[
        'State',
        '_HasNextOrEnd',
    ]:
        self.Next = state.ID
        self.End = None
        return state

    def parallel(
        self,
        branches=T.Iterable[T.Union['_HasNextOrEnd', 'StateMachine']],
    ) -> 'Parallel':
        sm_list: T.List[StateMachine] = list()
        for item in branches:
            if isinstance(item, _HasNextOrEnd):
                sm = _create_single_machine_from_state(item)
                sm_list.append(sm)
            elif isinstance(item, StateMachine):
                sm_list.append(item)
            else:
                raise TypeError
        para = Parallel(Branches=sm_list)
        self.next(para)
        return para

    def end(self):
        self.Next = None
        self.End = True


@attr.s
class _HasInputOutput(State):
    InputPath: T.Optional[str] = attr.ib(default=None)
    OutputPath: T.Optional[str] = attr.ib(default=None)


@attr.s
class _HasParameters(State):
    Parameters: T.Dict[str, T.Any] = attr.ib(factory=dict)


@attr.s
class _HasResultSelector(State):
    ResultSelector: T.Dict[str, T.Any] = attr.ib(factory=dict)


@attr.s
class _HasResultPath(State):
    ResultPath: T.Optional[str] = attr.ib(default=None)

    def use_task_result(self) -> T.Union[
        'Task', 'Parallel', 'Map', 'Pass'
    ]:
        self.ResultPath = "$"
        return self

    def discard_the_result_and_keep_original_input(self) -> T.Union[
        'Task', 'Parallel', 'Map', 'Pass'
    ]:
        self.ResultPath = "null"
        return self


@attr.s
class _RetryOrCatch(StepFunctionObject):
    ErrorEquals: T.List[str] = attr.ib(factory=list)

    def _pre_serialize_validation(self):
        for error_code in self.ErrorEquals:
            if not ErrorCodeEnum.contains(error_code):
                raise exc.StateValidationError

    def _add_error(self, error_code: str) -> '_RetryOrCatch':
        if error_code not in self.ErrorEquals:
            self.ErrorEquals.append(error_code)
        return self

    def at_all_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.AllError.value)

    def at_heartbeat_timeout_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.HeartbeatTimeoutError.value)

    def at_timeout_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.TimeoutError.value)

    def at_task_failed_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.TaskFailedError.value)

    def at_permissions_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.PermissionsError.value)

    def at_result_path_match_failure_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.ResultPathMatchFailureError.value)

    def at_parameter_path_failure_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.ParameterPathFailureError.value)

    def at_branch_failed_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.BranchFailedError.value)

    def at_no_choice_matched_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.NoChoiceMatchedError.value)

    def at_intrinsic_failure_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.IntrinsicFailureError.value)


@attr.s
class Retry(_RetryOrCatch):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html#error-handling-retrying-after-an-error
    """
    IntervalSeconds: int = attr.ib(default=None)
    BackoffRate: int = attr.ib(default=None)
    MaxAttempts: int = attr.ib(default=None)

    def with_interval_seconds(self, sec: int) -> 'Retry':
        self.IntervalSeconds = sec
        return self

    def with_back_off_rate(self, rate: int) -> 'Retry':
        self.BackoffRate = rate
        return self

    def with_max_attempts(self, attempts: int) -> 'Retry':
        self.MaxAttempts = attempts
        return self


@attr.s
class Catch(_RetryOrCatch):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html#error-handling-fallback-states
    """
    ResultPath: str = attr.ib(default=None)
    Next: str = attr.ib(default=None)

    def with_result_path(self, result_path: str):
        self.ResultPath = result_path
        return self

    def next(self, state: 'State') -> T.Union[
        'State', '_HasNextOrEnd',
    ]:
        self.Next = state.ID
        return state


@attr.s
class _HasRetryCatch(State):
    Retry: T.List['Retry'] = attr.ib(factory=list)
    Catch: T.List['Catch'] = attr.ib(factory=list)


@attr.s
class Task(
    _HasNextOrEnd,
    _HasInputOutput,
    _HasParameters,
    _HasResultSelector,
    _HasResultPath,
    _HasRetryCatch,
):
    ID: str = attr.ib(factory=lambda: f"{C.Task}-{short_uuid()}")
    Type: str = attr.ib(default=C.Task)

    Resource: T.Optional[str] = attr.ib(default=None)
    TimeoutSecondsPath: T.Optional[str] = attr.ib(default=None)
    TimeoutSeconds: T.Optional[int] = attr.ib(default=None)
    HeartbeatSecondsPath: T.Optional[str] = attr.ib(default=None)
    HeartbeatSeconds: T.Optional[int] = attr.ib(default=None)

    _key_order = [
        C.Type,
        C.Comment,

        C.Resource,
        C.Next,
        C.End,

        C.InputPath,
        C.Parameters,
        C.ResultSelector,
        C.ResultPath,
        C.OutputPath,

        C.Retry,
        C.Catch,
        C.TimeoutSecondsPath,
        C.TimeoutSeconds,
        C.HeartbeatSecondsPath,
        C.HeartbeatSeconds,
    ]


@attr.s
class Parallel(
    _HasNextOrEnd,
    _HasInputOutput,
    _HasParameters,
    _HasResultSelector,
    _HasResultPath,
    _HasRetryCatch,
):
    ID: str = attr.ib(factory=lambda: f"{C.Parallel}-{short_uuid()}")
    Type: str = attr.ib(default=C.Parallel)
    Branches: T.List['StateMachine'] = attr.ib(factory=list)

    _key_order = [
        C.Type,
        C.Comment,

        C.Branches,
        C.Next,
        C.End,

        C.InputPath,
        C.Parameters,
        C.ResultSelector,
        C.ResultPath,
        C.OutputPath,

        C.Retry,
        C.Catch,
    ]

    def _check_branches(self):
        if len(self.Branches) == 0:
            raise exc.StateValidationError(
                f"{C.Parallel!r} state can not have empty {C.Branches!r}!"
            )

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_branches()


    def _serialize(self) -> dict:
        data = self.to_dict()
        data.pop("ID")

        branches = list()
        for state_machine in self.Branches:
            dct = state_machine.serialize()
            branches.append(dct)
        data[C.Branches] = branches

        return data


class Map(
    _HasNextOrEnd,
    _HasInputOutput,
    _HasParameters,
    _HasResultSelector,
    _HasResultPath,
    _HasRetryCatch,
):
    _key_order = [
        C.Type,
        C.Comment,

        C.Branches,
        C.Next,
        C.End,

        C.InputPath,
        C.Parameters,
        C.ResultSelector,
        C.ResultPath,
        C.OutputPath,

        C.Retry,
        C.Catch,
    ]


class Pass(
    _HasInputOutput,
    _HasNextOrEnd,
    _HasResultPath,
    _HasParameters,
):
    ID: str = attr.ib(factory=lambda: f"{C.Pass.value}-{short_uuid()}")
    Type: str = attr.ib(default=C.Pass)

    _key_order = [
        C.Type,
        C.Comment,

        C.Next,
        C.End,

        C.InputPath,
        C.Parameters,
        C.ResultPath,
        C.OutputPath,
    ]


class Wait(
    _HasInputOutput,
    _HasNextOrEnd,
):
    ID: str = attr.ib(factory=lambda: f"{C.Wait}-{short_uuid()}")
    Type: str = attr.ib(default=C.Wait)

    _key_order = [
        C.Type,
        C.Comment,

        C.Next,
        C.End,

        C.InputPath,
        C.OutputPath,
    ]


@attr.s
class Option:
    pass


class Choice(
    _HasInputOutput
):
    ID: str = attr.ib(factory=lambda: f"{C.Choice}-{short_uuid()}")
    Type: str = attr.ib(default=C.Choice)
    Choices: T.List['Option'] = attr.ib(factory=list)

    _key_order = [
        C.Type,
        C.Comment,

        C.InputPath,
        C.OutputPath,
    ]

    def _pre_serialize_validation(self):
        if len(self.Choices) == 0:
            raise ValidationError


class Succeed(
    _HasInputOutput,
):
    ID: str = attr.ib(factory=lambda: f"{C.Succeed}-{short_uuid()}")
    Type: str = attr.ib(default=C.Succeed)

    _key_order = [
        C.Type,
        C.Comment,

        C.InputPath,
        C.OutputPath,
    ]


class Fail(
    State,
):
    ID: str = attr.ib(factory=lambda: f"{C.Fail}-{short_uuid()}")
    Type: str = attr.ib(default=C.Fail)

    _key_order = [
        C.Type,
        C.Comment,
    ]
