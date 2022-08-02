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
        self.envs[sm.id] = data

    def deregister(self, sm: "StateMachine"):
        pass


_context = Context()


class StateMachine(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    comment: str = Field(default="")
    start_at: str = Field(default="")
    states: list = Field(default_factory=list)
    version: str = Field(default="1.0")
    timeout_seconds: int = Field(default=0)

    _context_managed_attrs = [
        "comment",
        "start_at",
        "version",
        "timeout_seconds",
    ]

    def __enter__(self) -> "StateMachine":
        _context.register(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _context.deregister(self)
