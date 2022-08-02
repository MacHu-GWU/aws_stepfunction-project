# -*- coding: utf-8 -*-

import typing as T
import uuid
from collections import OrderedDict

import attr
from attr import (
    validators as vs,
    NOTHING,
)

from . import constant as C


@attr.s
class Context:
    queue: T.List['StateMachine'] = attr.ib(factory=list)

    def push(self, sm: "StateMachine"):
        # for k in sm.
        self.queue.append(sm)

    def pop(self, sm: "StateMachine"):
        self.queue.pop()


_context = Context()


def _to_dict(inst):
    return {
        k: v
        for k, v in attr.asdict(inst).items()
        if v is not None
    }


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
    ID: str = attr.ib(factory=lambda: str(uuid.uuid4()))
    StartAt: str = attr.ib(default="")
    Comment: T.Optional[str] = attr.ib(default=None)
    States: list = attr.ib(factory=list)
    Version: T.Optional[str] = attr.ib(default=None)
    TimeoutSeconds: T.Optional[int] = attr.ib(default=None)

    _states_mapper: T.Optional[OrderedDict] = attr.ib(factory=OrderedDict)

    def __enter__(self) -> "StateMachine":
        _context.push(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _context.pop(self)

    def add_state(self, state: 'State'):
        if state.ID in self._states_mapper:
            raise ValueError
        else:
            self.States.append(state)
            self._states_mapper[state.ID] = state

    def pre_serialize_validation(self):
        if not self.StartAt:
            raise InvalidStartAtError("StartAt cannot be empty string!")
        if self.StartAt not in self._states_mapper:
            raise InvalidStartAtError(
                f"StartAt id {self.StartAt!r} is not any of defined State ID"
            )

    def post_serialize_validation(self, data: dict):
        pass

    def serialize(
        self,
        skip_pre_validation=False,
        skip_post_validation=False,
    ) -> dict:
        if skip_pre_validation is False:
            self.pre_serialize_validation()
        data = _to_dict(self)
        data.pop("ID")
        data.pop("_states_mapper")
        if skip_post_validation is False:
            self.post_serialize_validation(data)
        return data


class State:
    Type: str = attr.ib()
    ID: str = attr.ib(factory=lambda: str(uuid.uuid4()))
    Comment: T.Optional[str] = attr.ib(default="")

    def pre_serialize_validation(self):
        pass

    def post_serialize_validation(self, data: dict):
        pass

    def serialize(
        self,
        skip_pre_validation=False,
        skip_post_validation=False,
    ) -> dict:
        if skip_pre_validation:
            self.pre_serialize_validation()
        data = _to_dict(self)
        if skip_post_validation:
            self.post_serialize_validation(data)
        return data


class Task(State):
    Type: str = attr.ib(default=C.StateTypeEnum.Task)

    Resource: str = attr.ib()
    TimeoutSecondsPath: T.Optional[str] = attr.ib(default=None)
    TimeoutSeconds: T.Optional[int] = attr.ib(default=None)
    HeartbeatSecondsPath: T.Optional[str] = attr.ib(default=None)
    HeartbeatSeconds: T.Optional[int] = attr.ib(default=None)

    Next: T.Optional[str] = attr.ib(default=None)
    End: T.Optional[bool] = attr.ib(default=False)
    InputPath: T.Optional[str] = attr.ib(default=None)
    OutputPath: T.Optional[str] = attr.ib(default=None)
    ResultPath: T.Optional[str] = attr.ib(default=None)
    Parameters: T.Optional[str] = attr.ib(default=None)
    ResultSelector: T.Optional[str] = attr.ib(default=None)
    Retry: T.Optional[str] = attr.ib(default=None)
    Catch: T.Optional[str] = attr.ib(default=None)


# Task()


class Parallel(State):
    pass


class Map(State):
    pass


class Pass(State):
    pass


class Wait(State):
    pass


class Choice(State):
    pass


class Succeeded(State):
    pass


class Fail(State):
    pass
