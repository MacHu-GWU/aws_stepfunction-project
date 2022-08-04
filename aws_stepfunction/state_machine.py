# -*- coding: utf-8 -*-

import typing as T
from collections import OrderedDict

import attr

from .constant import Constant as C
from .utils import short_uuid
from .model import StepFunctionObject
from . import exc

if T.TYPE_CHECKING:
    from .state import State


@attr.s
class Context:
    stack: T.List['StateMachine'] = attr.ib(factory=list)

    def push(self, sm: 'StateMachine'):
        self.stack.append(sm)

    def pop(self) -> 'StateMachine':
        return self.stack.pop()

    @property
    def current(self) -> 'StateMachine':
        return self.stack[-1]


_context = Context()

# ------------------------------------------------------------------------------
# StateMachine data model
# ------------------------------------------------------------------------------
__a_1_state_machine = None


@attr.s
class StateMachine(StepFunctionObject):
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

    def _pre_serialize_validation(self):
        if not self.StartAt:
            raise exc.StateMachineValidationError(
                f"StateMachine(ID={self.ID}): "
                f"'StartAt' cannot be empty string!"
            )
        if self.StartAt not in self.States:
            raise exc.StateMachineValidationError(
                f"StateMachine(ID={self.ID}): "
                f"'StartAt' id {self.StartAt!r} is not any of defined State ID"
            )

    def _serialize(self) -> dict:
        data = {
            C.StartAt: self.StartAt,
            C.States: {
                state_id: state._serialize()
                for state_id, state in self.States.items()
            },
        }
        if self.Comment:
            data[C.Comment] = self.Comment
        if self.Version:
            data[C.Version] = self.Version
        if self.Version:
            data[C.TimeoutSeconds] = self.TimeoutSeconds
        return data
