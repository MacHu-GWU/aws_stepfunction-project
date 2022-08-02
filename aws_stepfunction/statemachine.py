# -*- coding: utf-8 -*-

import typing as T
import uuid
from collections import OrderedDict

from pydantic import BaseModel, Field, PrivateAttr, validator

from . import constant as C


class Context(BaseModel):
    queue: T.List['StateMachine'] = Field(default_factory=list)

    def push(self, sm: "StateMachine"):
        # for k in sm.
        self.queue.append(sm)

    def pop(self, sm: "StateMachine"):
        self.queue.pop()


_context = Context()


class StateMachine(BaseModel):
    ID: str = Field(default_factory=lambda: str(uuid.uuid4()))
    StartAt: str = Field(default="")
    Comment: T.Optional[str] = Field(default=None)
    States: list = Field(default_factory=list)
    Version: T.Optional[str] = Field(default=None)
    TimeoutSeconds: T.Optional[int] = Field(default=None)

    _states_mapper: T.Optional[OrderedDict] = PrivateAttr(default_factory=OrderedDict)

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
        data = self.dict(
            exclude={"_states_mapper", },
            exclude_none=True,
        )
        if skip_post_validation:
            self.post_serialize_validation(data)
        return data


class State(BaseModel):
    Type: str = Field()
    ID: str = Field(default_factory=lambda: str(uuid.uuid4()))
    Comment: T.Optional[str] = Field(default="")

    @validator("ID")
    def check_ID(cls, v):
        sm = _context.queue[-1]
        sm.add_state()
        return v

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
        data = self.dict(exclude_none=True)
        if skip_post_validation:
            self.post_serialize_validation(data)
        return data


class Task(State):
    Type: str = Field(default=C.StateTypeEnum.Task)

    Resource: str = Field()
    TimeoutSecondsPath: T.Optional[str] = Field(default=None)
    TimeoutSeconds: T.Optional[int] = Field(default=None)
    HeartbeatSecondsPath: T.Optional[str] = Field(default=None)
    HeartbeatSeconds: T.Optional[int] = Field(default=None)

    Next: T.Optional[str] = Field(default=None)
    End: T.Optional[bool] = Field(default=False)
    InputPath: T.Optional[str] = Field(default=None)
    OutputPath: T.Optional[str] = Field(default=None)
    ResultPath: T.Optional[str] = Field(default=None)
    Parameters: T.Optional[str] = Field(default=None)
    ResultSelector: T.Optional[str] = Field(default=None)
    Retry: T.Optional[str] = Field(default=None)
    Catch: T.Optional[str] = Field(default=None)


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
