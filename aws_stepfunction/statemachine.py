# -*- coding: utf-8 -*-

import typing as T
import uuid

from pydantic import BaseModel, Field

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
    Comment: str = Field(default="")
    StartAt: str = Field(default="")
    States: list = Field(default_factory=list)
    Version: str = Field(default="1.0")
    TimeoutSeconds: int = Field(default=0)

    _context_managed_attrs = [
        "Comment",
        "StartAt",
        "Version",
        "TimeoutSeconds",
    ]

    def __enter__(self) -> "StateMachine":
        _context.push(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _context.pop(self)


class State(BaseModel):
    Type: str = Field()
    Comment: T.Optional[str] = Field(default="")


class Task(State):
    Type: str = Field(default=C.StateTypeEnum.Task)
    End: str = Field(default=False)


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
