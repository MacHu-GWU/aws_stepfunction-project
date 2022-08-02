# -*- coding: utf-8 -*-

import typing as T
import uuid
import dataclasses as dc

from pydantic import BaseModel, Field


@dc.dataclass
class Context:
    envs: T.Dict[str, T.Dict[str, T.Any]] = dc.field(default_factory=dict)

    def register(self, sm: "StateMachine"):
        # for k in sm.
        data = {attr: getattr(sm, attr) for attr in StateMachine._context_managed_attrs}
        self.envs[sm.ID] = data

    def deregister(self, sm: "StateMachine"):
        pass


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
        _context.register(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _context.deregister(self)


class State(BaseModel):
    pass


class Task(State):
    pass


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
