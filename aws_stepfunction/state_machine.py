# -*- coding: utf-8 -*-

import typing as T
from collections import OrderedDict, deque
from rich import print as rprint
import attr

from . import exc
from .constant import Constant as C
from .utils import short_uuid
from .model import StepFunctionObject
from .choice_rule import ChoiceRule
from .state import (
    StateType, Task, Parallel, Map, Pass, Wait, Choice, Succeed, Fail
)

# ------------------------------------------------------------------------------
# StateMachine data model
# ------------------------------------------------------------------------------
__a_1_state_machine = None


@attr.s
class StateMachine(StepFunctionObject):
    id: str = attr.ib(factory=lambda: f"StateMachine-{short_uuid()}")
    start_at: str = attr.ib(default="")
    comment: T.Optional[str] = attr.ib(default=None)
    states: T.OrderedDict[str, 'StateType'] = attr.ib(factory=OrderedDict)
    version: T.Optional[str] = attr.ib(default=None)
    timeout_seconds: T.Optional[int] = attr.ib(default=None)

    _previous_state: T.Optional['StateType'] = attr.ib(default=None)

    def add_state(self, state: 'StateType'):
        if state.id in self.states:
            raise exc.StateMachineError.make(
                self,
                f"Cannot add State(ID={state.id!r}), "
                f"It is already defined!"
            )
        else:
            self.states[state.id] = state

    def remove_state(self, state: 'StateType'):
        if state.id not in self.states:
            raise exc.StateMachineError.make(
                self, ""
            )
        else:
            self.states.pop(state.id)
            state._state_machine = {state.id}

    # Workflow
    def start(self, state: 'StateType'):
        self.start_at = state.id
        self.add_state(state)
        self._previous_state = state
        return self

    def next_then(self, state: 'StateType'):
        self._previous_state.next = state.id
        if state.id not in self.states:
            self.add_state(state)
        self._previous_state = state
        return self

    def parallel_from(self, state: 'StateType') -> 'StateMachine':
        sm = StateMachine()
        sm.start(state)
        return sm

    def parallel(
        self,
        branches: T.Iterable['StateMachine'],
        id: T.Optional[str] = None,
    ):
        kwargs = dict(branches=branches)
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Parallel}-after-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        parallel = Parallel(**kwargs)
        self._previous_state.next = parallel.id
        rprint(self._previous_state)
        self.add_state(parallel)
        self._previous_state = parallel
        return self

    def map_from(self, state: 'StateType') -> 'StateMachine':
        sm = StateMachine()
        sm.start(state)
        return sm

    def map(
        self,
        iterator: 'StateMachine',
        items_path: T.Optional[str] = None,
        max_concurrency: T.Optional[int] = None,
        id: T.Optional[str] = None,
    ):
        kwargs = dict(
            iterator=iterator,
            items_path=items_path,
            max_concurrency=max_concurrency,
        )
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Map}-after-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        map_ = Map(**kwargs)
        self._previous_state.next = map_.id
        rprint(self._previous_state)
        self.add_state(map_)
        self._previous_state = map_
        return self

    def choice(
        self,
        choices: T.List['ChoiceRule'],
        default: T.Optional['StateType'] = None,
        id: T.Optional[str] = None
    ) -> 'Choice':
        kwargs = dict(choices=choices)
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Choice}-by-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        if default is not None:
            kwargs["default"] = default.id
        choice = Choice(
            **kwargs
        )
        self._previous_state.next = choice.id
        self.add_state(choice)
        self._previous_state = choice
        return choice

    def wait(
        self,
        id: T.Optional[str] = None,
        seconds: T.Optional[int] = None,
        timestamp: T.Optional[str] = None,
        seconds_path: T.Optional[str] = None,
        timestamp_path: T.Optional[str] = None,
    ):
        kwargs = dict(
            seconds=seconds,
            timestamp=timestamp,
            seconds_path=seconds_path,
            timestamp_path=timestamp_path,
        )
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Wait}-after-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        wait = Wait(**kwargs)
        self._previous_state.next = wait.id
        self.add_state(wait)
        self._previous_state = wait
        return self

    #
    # def passing(self) -> 'Pass':
    #     pass
    #
    def succeed(self):
        kwargs = dict()
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Succeed}-after-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        succeed = Succeed(**kwargs)
        self.add_state(succeed)
        self._previous_state = succeed
        return self

    def fail(
        self,
        cause: T.Optional[str] = None,
        error: T.Optional[str] = None,
        id: T.Optional[str] = None,
    ):
        kwargs = dict(cause=cause, error=error)
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Fail}-after-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        fail = Fail(**kwargs)
        self.add_state(fail)
        self._previous_state = fail
        return self

    def end(self):
        self._previous_state.end = True
        return self

    def continue_from(self, state: 'StateType'):
        if state.id not in self.states:
            self.add_state(state)
        self._previous_state = state
        return self

    def _pre_serialize_validation(self):
        if not self.start_at:
            raise exc.StateMachineValidationError.make(
                self,
                f"'StartAt' cannot be empty string!"
            )
        if self.start_at not in self.states:
            raise exc.StateMachineValidationError(
                self,
                f"'StartAt' id {self.start_at!r} is not any of defined State ID"
            )

    def _serialize(self) -> dict:
        data = {
            C.StartAt: self.start_at,
            C.States: {
                state_id: state.serialize()
                for state_id, state in self.states.items()
            },
        }

        if self.comment:
            data[C.Comment] = self.comment
        if self.version:
            data[C.Version] = self.version
        if self.timeout_seconds:
            data[C.TimeoutSeconds] = self.timeout_seconds

        return data
