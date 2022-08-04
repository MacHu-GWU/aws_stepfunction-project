# -*- coding: utf-8 -*-

import typing as T

import attr

from . import exc
from .constant import (
    Constant as C,
    ErrorCodeEnum,
)
from .utils import short_uuid, is_json_path
from .model import StepFunctionObject
from .choice_rule import ChoiceRule
from .state_machine import _context, StateMachine


# ------------------------------------------------------------------------------
# State Data Model
# ------------------------------------------------------------------------------
@attr.s
class State(StepFunctionObject):
    """
    :param _uuid: for internal implementation. we track the associated
        state machine of each state object.

    Serialization Field Order:

    1. 先展示信息量最大的, 例如 Type, Comment
    2. 再展示跟当前 State 的逻辑紧密相关的, 例如 Task 就需要关注 Resource,
        Parallel 就需要关注 Branches, Map 就需要关注 Iterator 等等
    3. 接下来展示跟流程相关的 Next, End
    4. 最后展示详细的 Input Output 处理的细节
    """
    ID: str = attr.ib(factory=lambda: short_uuid())
    Type: str = attr.ib(default=None)
    Comment: T.Optional[str] = attr.ib(default=None)

    _uuid: T.Optional[str] = attr.ib(default=None)

    def __attrs_post_init__(self):
        """
        .. code-block:: python

            # automatically add the task to the state machine
            with StateMachine() as sm:
                task = Task(...)
        """
        self._uuid = self.ID
        if len(_context.stack):
            sm = _context.stack[-1]
            sm.add_state(self)

    @property
    def _state_machine_id(self) -> T.Optional[str]:
        if C.Sep in self._uuid:
            return self._uuid.split(C.Sep, 1)[0]
        else:
            return None

    def _serialize(self) -> dict:
        data = self.to_dict()
        data.pop("ID")
        data.pop("_uuid")
        if data.get(C.ResultPath, None) == "null":
            data[C.ResultPath] = None
        return data

    # since json path attribute is so common,
    # we should create a validator for that
    def _check_json_path(self, attr: str, value: str):
        if not is_json_path(value):
            raise exc.StateValidationError.make(
                self,
                (
                    f"State.{attr} = {value!r} is not a valid JSON path!"
                )
            )

    def _check_opt_json_path(self, attr: str, value: T.Optional[str]):
        if value is not None:
            self._check_json_path(attr, value)


def _create_single_machine_from_state(state: '_HasNextOrEnd') -> 'StateMachine':
    """
    """
    # create a new state machine based on given state
    with StateMachine() as new_sm:
        new_sm._is_parallel_branch = True
        new_sm.add_state(state)
        new_sm.set_start_at(state)
        state.end()

    # un-associate the given state from its old state machine
    old_sm = _context.find_state_owner(state)
    if old_sm is not None:
        old_sm.remove_state(state)

    return new_sm


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

    def _check_input_output_path(self):
        self._check_opt_json_path(C.InputPath, self.InputPath)
        self._check_opt_json_path(C.OutputPath, self.OutputPath)


@attr.s
class _HasParameters(State):
    Parameters: T.Dict[str, T.Any] = attr.ib(factory=dict)


@attr.s
class _HasResultSelector(State):
    ResultSelector: T.Dict[str, T.Any] = attr.ib(factory=dict)


@attr.s
class _HasResultPath(State):
    ResultPath: T.Optional[str] = attr.ib(default=None)

    def _check_result_path(self):
        if self.ResultPath is not None:
            if self.ResultPath != "null":
                self._check_json_path(C.ResultPath, self.ResultPath)

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
        C.TimeoutSeconds,
        C.TimeoutSecondsPath,
        C.HeartbeatSeconds,
        C.HeartbeatSecondsPath,

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

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()
        self._check_result_path()

        self._check_opt_json_path(C.TimeoutSecondsPath, self.TimeoutSecondsPath)
        self._check_opt_json_path(C.HeartbeatSecondsPath, self.HeartbeatSecondsPath)


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
        self._check_input_output_path()
        self._check_result_path()

        self._check_branches()

    def _serialize(self) -> dict:
        data = super()._serialize()

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
    ID: str = attr.ib(factory=lambda: f"{C.Map}-{short_uuid()}")
    Type: str = attr.ib(default=C.Map)
    Iterator: T.Optional['StateMachine'] = attr.ib(default=None)
    ItemsPath: T.Optional['str'] = attr.ib(default=None)
    MaxConcurrency: T.Optional[int] = attr.ib(default=None)

    _key_order = [
        C.Type,
        C.Comment,

        C.Iterator,
        C.ItemsPath,
        C.MaxConcurrency,

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

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()
        self._check_result_path()

        self._check_opt_json_path(C.ItemsPath, self.ItemsPath)


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

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()
        self._check_result_path()


class Wait(
    _HasInputOutput,
    _HasNextOrEnd,
):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-wait-state.html
    """
    ID: str = attr.ib(factory=lambda: f"{C.Wait}-{short_uuid()}")
    Type: str = attr.ib(default=C.Wait)

    Seconds: T.Optional[int] = attr.ib(default=None)
    Timestamp: T.Optional[str] = attr.ib(default=None)
    SecondsPath: T.Optional[str] = attr.ib(default=None)
    TimestampPath: T.Optional[str] = attr.ib(default=None)

    _key_order = [
        C.Type,
        C.Comment,

        C.Seconds,
        C.Timestamp,
        C.SecondsPath,
        C.TimestampPath,

        C.Next,
        C.End,

        C.InputPath,
        C.OutputPath,
    ]

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()


class Choice(
    _HasInputOutput
):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-choice-state.html
    """
    ID: str = attr.ib(factory=lambda: f"{C.Choice}-{short_uuid()}")
    Type: str = attr.ib(default=C.Choice)
    Choices: T.List['ChoiceRule'] = attr.ib(factory=list)
    Default: T.Optional[str] = attr.ib(default=None)

    _key_order = [
        C.Type,
        C.Comment,

        C.Choices,
        C.Default,

        C.InputPath,
        C.OutputPath,
    ]

    def _check_choices(self):
        if len(self.Choices) == 0:
            raise exc.StateValidationError

    def _pre_serialize_validation(self):
        self._check_input_output_path()

        self._check_choices()


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

    def _pre_serialize_validation(self):
        self._check_input_output_path()


class Fail(
    State,
):
    ID: str = attr.ib(factory=lambda: f"{C.Fail}-{short_uuid()}")
    Type: str = attr.ib(default=C.Fail)
    Cause: T.Optional[str] = attr.ib(default=None)
    Error: T.Optional[str] = attr.ib(default=None)

    _key_order = [
        C.Type,
        C.Comment,

        C.Cause,
        C.Error,
    ]
