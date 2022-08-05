# -*- coding: utf-8 -*-

import typing as T
from collections import OrderedDict, deque

import attr

from .constant import Constant as C
from .utils import short_uuid
from .model import StepFunctionObject
from . import exc

if T.TYPE_CHECKING:
    from .state import StateType


@attr.s
class Context:
    """
    :param stack: track the current top level state machine
    :param state_machines: all declared state machine metadata
    """
    stack: T.List['StateMachine'] = attr.ib(factory=list)
    state_machines: T.Dict[str, 'StateMachine'] = attr.ib(factory=dict)

    def push(self, sm: 'StateMachine'):
        self.stack.append(sm)
        self.state_machines[sm.ID] = sm

    def pop(self) -> 'StateMachine':
        sm = self.stack.pop()
        return sm

    @property
    def current(self) -> 'StateMachine':
        return self.stack[-1]

    def find_state_owner(self, state: 'State') -> T.Optional['StateMachine']:
        if state._state_machine_id is None:
            return None
        else:
            return self.state_machines[state._state_machine_id]


_context = Context()

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

    _is_parallel_branch: bool = attr.ib(default=False)
    _state_orders: T.Deque[str] = attr.ib(factory=deque)

    def __enter__(self) -> 'StateMachine':
        _context.push(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        _context.pop()

    def add_state(self, state: 'StateType'):
        if state.id in self.states:
            raise exc.StateMachineError.make(
                self,
                f"Cannot add State(ID={state.id!r}), "
                f"It is already defined!"
            )
        else:
            self.states[state.id] = state
            # state._uuid = f"{self.ID}{C.Sep}{state.id}"

    def remove_state(self, state: 'StateType'):
        if state.id not in self.states:
            raise exc.StateMachineError.make(
                self, ""
            )
        else:
            self.states.pop(state.id)
            state._state_machine = {state.id}

    def set_start_at(self, state: 'StateType'):
        self.StartAt = state.id

    # Workflow
    def start(self, state: 'StateType'):
        self.start_at = state.id
        self.add_state(state)
        self._previous_state = state
        return self

    def next(self, state: 'StateType'):
        self._previous_state.next = state.id
        self.add_state(state)
        self._previous_state = state
        return self

    #
    # def parallel(
    #     self,
    #     branches: T.Iterable[T.Union['StateType', 'StateMachine']],
    #     id: T.Optional[str] = None,
    # ) -> 'Parallel':
    #     state_machine_list: T.List[StateMachine] = list()
    #     for item in branches:
    #         if isinstance(item, _HasNextOrEnd):
    #             state_machine = _create_single_machine_from_state(item)
    #             state_machine_list.append(state_machine)
    #         elif isinstance(item, StateMachine):
    #             state_machine_list.append(item)
    #         else:
    #             raise TypeError
    #
    #     kwargs = {C.Branches: state_machine_list}
    #     if id is not None:
    #         kwargs[C.ID] = id
    #
    #     para = Parallel(**kwargs)
    #     self.next(para)
    #     return para
    #
    # def map(
    #     self,
    #     iterator: T.Union['StateType', 'StateMachine'],
    #     items_path: T.Optional[str] = None,
    # ) -> 'Map':
    #     pass
    #
    def choice(
        self,
        choices: T.Iterable[T.Union['StateType', 'StateMachine']],
        default: T.Optional['StateType'] = None,
    ):
        return self
    #
    # def wait(self, seconds: int) -> 'Wait':
    #     pass
    #
    # def passing(self) -> 'Pass':
    #     pass
    #
    # def succeed(self) -> 'Succeed':
    #     pass
    #
    # def fail(self) -> 'Fail':
    #     pass
    #
    def end(self):
        self._previous_state.end = True
        return self

    def continue_from(self, state: 'StateType') -> 'StateType':
        return state

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
        if self._is_parallel_branch is True:
            return data

        if self.comment:
            data[C.Comment] = self.comment
        if self.version:
            data[C.Version] = self.version
        if self.timeout_seconds:
            data[C.TimeoutSeconds] = self.timeout_seconds

        return data
