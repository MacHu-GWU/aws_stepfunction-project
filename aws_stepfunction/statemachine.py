# -*- coding: utf-8 -*-

import typing as T
from collections import OrderedDict

import attr
from attr import (
    validators as vs,
)

from . import constant as C
from .utils import short_uuid


@attr.s
class Context:
    stack: T.List['StateMachine'] = attr.ib(factory=list)

    def push(self, sm: 'StateMachine'):
        # for k in sm.
        self.stack.append(sm)

    def pop(self) -> 'StateMachine':
        return self.stack.pop()

    @property
    def current(self) -> 'StateMachine':
        return self.stack[-1]


_context = Context()


def _to_dict(inst):
    dct = dict()
    for k, v in attr.asdict(inst).items():
        if isinstance(v, (list, dict)):
            if len(v):
                dct[k] = v
        elif v is not None:
            dct[k] = v
    return dct


# ------------------------------------------------------------------------------
# Validation Errors
# ------------------------------------------------------------------------------
class ValidationError(Exception):
    @classmethod
    def _make(cls, msg: str) -> 'ValidationError':
        return cls(msg)


# ------------------------------------------------------------------------------
# StateMachine data model
# ------------------------------------------------------------------------------
__a_1_state_machine = None


class InvalidStartAtError(ValidationError):
    pass


@attr.s
class StateMachine:
    ID: str = attr.ib(factory=lambda: f"StateMachine-{short_uuid()}")
    StartAt: str = attr.ib(default="")
    Comment: T.Optional[str] = attr.ib(default=None)
    States: T.OrderedDict[str, 'State'] = attr.ib(factory=OrderedDict)
    Version: T.Optional[str] = attr.ib(default=None)
    TimeoutSeconds: T.Optional[int] = attr.ib(default=None)

    _is_parallel_branch: bool = attr.ib(default=False)

    def __enter__(self) -> 'StateMachine':
        _context.push(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _context.pop()

    def add_state(self, state: 'State'):
        if state.ID in self.States:
            raise ValueError
        else:
            self.States[state.ID] = state

    def set_start_at(self, state: 'State'):
        self.StartAt = state.ID

    def pre_serialize_validation(self):
        if not self.StartAt:
            raise InvalidStartAtError(
                f"StateMachine(ID={self.ID}): 'StartAt' cannot be empty string!"
            )
        if self.StartAt not in self.States:
            raise InvalidStartAtError(
                f"StateMachine(ID={self.ID}): 'StartAt' id {self.StartAt!r} is not any of defined State ID"
            )

    def post_serialize_validation(self, data: dict):
        pass

    def serialize(
        self,
        do_pre_validation=True,
        do_post_validation=True,
    ) -> dict:
        if do_pre_validation:
            self.pre_serialize_validation()
        data = {
            C.TopLevelFieldEnum.StartAt.value: self.StartAt,
            C.TopLevelFieldEnum.States.value: {
                state_id: state._serialize()
                for state_id, state in self.States.items()
            },
        }
        if self.Comment:
            data[C.TopLevelFieldEnum.Comment] = self.Comment
        if self.Version:
            data[C.TopLevelFieldEnum.Version] = self.Version
        if self.Version:
            data[C.TopLevelFieldEnum.TimeoutSeconds] = self.TimeoutSeconds
        if do_post_validation:
            self.post_serialize_validation(data)
        return data


# ------------------------------------------------------------------------------
# State Related Validators
# ------------------------------------------------------------------------------
def _check_next_and_end(state: '_HasNextOrEnd'):
    if state.End is True:
        if state.Next:
            # when "End" is True, you can NOT have "Next"
            raise ValueError
    else:
        if not state.Next:
            # when "End" is not True, you HAVE TO have "Next"
            raise ValueError


# ------------------------------------------------------------------------------
# State Data Model
# ------------------------------------------------------------------------------
@attr.s
class State:
    ID: str = attr.ib(factory=lambda: short_uuid())
    Type: str = attr.ib(default=None)
    Comment: T.Optional[str] = attr.ib(default=None)

    _key_order: T.List[str] = []

    def __attrs_post_init__(self):
        if len(_context.stack):
            sm = _context.stack[-1]
            sm.add_state(self)

    def _pre_serialize_validation(self):
        pass

    def _post_serialize_validation(self, data: dict):
        pass

    @classmethod
    def _reorder(cls, data: dict) -> dict:
        ordered_data = dict()
        for key in cls._key_order:
            if key in data:
                ordered_data[key] = data[key]
        return ordered_data

    def _serialize(
        self,
        do_pre_validation=True,
        do_post_validation=True,
    ) -> dict:
        if do_pre_validation:
            self._pre_serialize_validation()
        data = _to_dict(self)
        data.pop("ID")
        new_data = self._reorder(data)
        if do_post_validation:
            self._post_serialize_validation(new_data)
        return new_data


def _create_single_machine_from_state(state: '_HasNextOrEnd') -> 'StateMachine':
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

    def pre_serialize_validation(self):
        _check_next_and_end(self)

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
class _HasResultPath(State):
    ResultPath: T.Optional[str] = attr.ib(default=None)


@attr.s
class _HasResultSelector(State):
    ResultSelector: T.Dict[str, T.Any] = attr.ib(factory=dict)


@attr.s
class Retry:
    ErrorEquals: T.List[str] = attr.ib(factory=None)
    IntervalSeconds: int = attr.ib(default=None)
    BackoffRate: int = attr.ib(default=None)
    MaxAttempts: int = attr.ib(default=None)


@attr.s
class Catch:
    ErrorEquals: T.List[str] = attr.ib(default=None)
    ResultPath: str = attr.ib(default=None)
    Next: str = attr.ib(default=None)

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
    _HasInputOutput,
    _HasNextOrEnd,
    _HasResultPath,
    _HasParameters,
    _HasResultSelector,
    _HasRetryCatch,
):
    ID: str = attr.ib(factory=lambda: f"{C.StateTypeEnum.Task.value}-{short_uuid()}")
    Type: str = attr.ib(default=C.StateTypeEnum.Task.value)

    Resource: T.Optional[str] = attr.ib(default=None)
    TimeoutSecondsPath: T.Optional[str] = attr.ib(default=None)
    TimeoutSeconds: T.Optional[int] = attr.ib(default=None)
    HeartbeatSecondsPath: T.Optional[str] = attr.ib(default=None)
    HeartbeatSeconds: T.Optional[int] = attr.ib(default=None)

    _key_order = [
        C.Enum.Type.value,
        C.Enum.Comment.value,

        C.Enum.Resource.value,
        C.Enum.Next.value,
        C.Enum.End.value,

        C.Enum.InputPath.value,
        C.Enum.OutputPath.value,
        C.Enum.ResultPath.value,
        C.Enum.Parameters.value,
        C.Enum.ResultSelector.value,
        C.Enum.Retry.value,
        C.Enum.Catch.value,
        C.Enum.TimeoutSecondsPath.value,
        C.Enum.TimeoutSeconds.value,
        C.Enum.HeartbeatSecondsPath.value,
        C.Enum.HeartbeatSeconds.value,
    ]


@attr.s
class Parallel(
    _HasInputOutput,
    _HasNextOrEnd,
    _HasResultPath,
    _HasParameters,
    _HasResultSelector,
    _HasRetryCatch,
):
    ID: str = attr.ib(factory=lambda: f"{C.StateTypeEnum.Parallel.value}-{short_uuid()}")
    Type: str = attr.ib(default=C.StateTypeEnum.Parallel.value)
    Branches: T.List['StateMachine'] = attr.ib(factory=list)

    _key_order = [
        C.Enum.Type.value,
        C.Enum.Comment.value,

        C.Enum.Branches.value,
        C.Enum.Next.value,
        C.Enum.End.value,

        C.Enum.InputPath.value,
        C.Enum.OutputPath.value,
        C.Enum.ResultPath.value,
        C.Enum.Parameters.value,
        C.Enum.ResultSelector.value,
        C.Enum.Retry.value,
        C.Enum.Catch.value,
    ]

    def _serialize(
        self,
        do_pre_validation=True,
        do_post_validation=True,
    ) -> dict:
        if do_pre_validation:
            self.pre_serialize_validation()
        data = _to_dict(self)
        data.pop("ID")

        branches = list()
        for sm in self.Branches:
            dct = sm.serialize()
            branches.append(dct)
        data[C.Enum.Branches.value] = branches

        if do_post_validation:
            self._post_serialize_validation(data)
        return data


class Map(State):
    pass


class Pass(
    _HasInputOutput,
    _HasNextOrEnd,
    _HasResultPath,
    _HasParameters,
):
    ID: str = attr.ib(factory=lambda: f"{C.StateTypeEnum.Pass.value}-{short_uuid()}")
    Type: str = attr.ib(default=C.StateTypeEnum.Pass.value)

    _key_order = [
        C.Enum.Type.value,
        C.Enum.Comment.value,

        C.Enum.Next.value,
        C.Enum.End.value,

        C.Enum.InputPath.value,
        C.Enum.OutputPath.value,
        C.Enum.ResultPath.value,
        C.Enum.Parameters.value,
    ]


class Wait(
    _HasInputOutput,
    _HasNextOrEnd,
):
    ID: str = attr.ib(factory=lambda: f"{C.StateTypeEnum.Wait.value}-{short_uuid()}")
    Type: str = attr.ib(default=C.StateTypeEnum.Wait.value)

    _key_order = [
        C.Enum.Type.value,
        C.Enum.Comment.value,

        C.Enum.Next.value,
        C.Enum.End.value,

        C.Enum.InputPath.value,
        C.Enum.OutputPath.value,
    ]


class Choice(
    _HasInputOutput
):
    ID: str = attr.ib(factory=lambda: f"{C.StateTypeEnum.Choice.value}-{short_uuid()}")
    Type: str = attr.ib(default=C.StateTypeEnum.Choice.value)

    _key_order = [
        C.Enum.Type.value,
        C.Enum.Comment.value,

        C.Enum.InputPath.value,
        C.Enum.OutputPath.value,
    ]


class Succeeded(State):
    pass


class Fail(State):
    pass


class _End:
    pass


END = _End()
