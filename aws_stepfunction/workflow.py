# -*- coding: utf-8 -*-

"""

"""

import typing as T

import attr
import attr.validators as vs

from . import exc
from .constant import Constant as C
from .utils import short_uuid
from .model import StepFunctionObject
from .choice_rule import ChoiceRule
from .state import (
    StateType, Task, Parallel, Map, Pass, Wait, Choice, Succeed, Fail
)


@attr.s
class Workflow(StepFunctionObject):
    """
    Workflow is a series of event-driven steps.

    This class defines the transition logic from one step to another.

    :param id:
    :param start_at:
    :param comment:
    :param states:
    :param version:
    :param timeout_seconds:

    Reference:

    - https://states-language.net/spec.html#toplevelfields
    """
    id: str = attr.ib(
        factory=lambda: f"Workflow-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    comment: T.Optional[str] = attr.ib(
        default=None,
        validator=vs.optional(vs.instance_of(str)),
    )
    version: T.Optional[str] = attr.ib(
        default=None,
        validator=vs.optional(vs.instance_of(str)),
    )
    timeout_seconds: T.Optional[int] = attr.ib(
        default=None,
        validator=vs.optional(vs.instance_of(int)),
    )

    _start_at: T.Optional[str] = attr.ib(
        default=None,
        validator=vs.optional(vs.instance_of(str)),
    )
    _states: T.Dict[str, 'StateType'] = attr.ib(
        factory=dict,
        validator=vs.deep_mapping(
            key_validator=vs.instance_of(str),
            value_validator=vs.instance_of(StateType),
        ),
    )

    _started: bool = attr.ib(default=False)
    _previous_state: T.Optional['StateType'] = attr.ib(default=None)

    _field_order = [
        C.Version,
        C.StartAt,
        C.Comment,
        C.TimeoutSeconds,
        C.States,
    ]

    def _add_state(
        self,
        state: 'StateType',
        ignore_exists: bool = False,
    ) -> bool:
        """
        Add a new state to this workflow.

        :rtype: indicate whether a new state is added
        """
        if state.id in self._states:
            if ignore_exists is False:
                raise exc.WorkflowError.make(
                    self,
                    f"Cannot add State(ID={state.id!r}), "
                    f"it is already defined!"
                )
            return False
        else:
            self._states[state.id] = state
            return True

    def _remove_state(
        self,
        state: 'StateType',
        ignore_not_exists: bool = False,
    ) -> bool:
        """
        Remove a state from workflow.

        :rtype: indicate whether a state is removed
        """
        if state.id not in self._states:
            if ignore_not_exists is False:
                raise exc.WorkflowError.make(
                    self,
                    f"Cannot remove State(ID={state.id!r}), "
                    f"it doesn't exist!"
                )
            return False
        else:
            self._states.pop(state.id)
            return True

    def _parallel(
        self,
        branches: T.Iterable['Workflow'],
        id: T.Optional[str] = None,
    ) -> 'Parallel':
        """
        Construct a :class:`aws_stepfunction.state.Parallel` task.
        """
        kwargs = dict(branches=branches)
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Parallel}-after-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        parallel = Parallel(**kwargs)
        return parallel

    def _map(
        self,
        iterator: 'Workflow',
        items_path: T.Optional[str] = None,
        max_concurrency: T.Optional[int] = None,
        id: T.Optional[str] = None,
    ) -> 'Map':
        """
        Construct a :class:`aws_stepfunction.state.Map` task.
        """
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
        return map_

    def _choice(
        self,
        choices: T.List['ChoiceRule'],
        default: T.Optional['StateType'] = None,
        id: T.Optional[str] = None
    ) -> 'Choice':
        """
        Construct a :class:`aws_stepfunction.state.Choice` task.
        """
        kwargs = dict(choices=choices)
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Choice}-by-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        if default is not None:
            kwargs["default"] = default.id
        choice = Choice(**kwargs)
        return choice

    def subflow_from(self, state: 'StateType') -> 'Workflow':
        """
        Similar to :meth:`Workflow.start_from`, but it creates a new
        workflow instance and start from there.
        """
        workflow = Workflow()
        workflow.start_from(state)
        return workflow

    def start_from(self, state: 'StateType') -> 'Workflow':
        """
        Start the workflow from a state.
        """
        self._start_at = state.id
        self._add_state(state)
        self._started = True
        self._previous_state = state
        return self

    def _check_started(self):
        if self._started is not True:
            raise exc.WorkflowError.make(
                self,
                "the workflow is not started yet, "
                "you should call one of the "
                "'Workflow.start()' "
                "'Workflow.start_from_parallel()' "
                "'Workflow.start_from_map()' "
                "'Workflow.start_from_choice()' "
                "first!"
            )
        elif self._previous_state is None:
            raise exc.WorkflowError.make(
                self,
                f"looks like you just defined a '{C.Choice}' state, "
                "you cannot call 'next_then()' immediately. because the workflow "
                "doesn't know which branch to continue from. "
                "you should call 'Workflow.continue_from()' for the first task "
                "of  each choice branch to continue orchestration."
            )

    def next_then(self, state: 'StateType') -> 'Workflow':
        """
        Move from previous state to the next state.
        """
        self._check_started()
        self._previous_state.next = state.id
        if state.id not in self._states:
            self._add_state(state)
        self._previous_state = state
        return self

    def start_from_parallel(
        self,
        branches: T.Iterable['Workflow'],
        id: T.Optional[str] = None,
    ) -> 'Workflow':
        """

        """
        parallel = self._parallel(branches=branches, id=id)
        self._start_at = parallel.id
        self._add_state(parallel)
        self._started = True
        self._previous_state = parallel
        return self

    def parallel(
        self,
        branches: T.Iterable['Workflow'],
        id: T.Optional[str] = None,
    ) -> 'Workflow':
        """

        """
        self._check_started()
        parallel = self._parallel(branches=branches, id=id)
        self._previous_state.next = parallel.id
        self._add_state(parallel)
        self._started = True
        self._previous_state = parallel
        return self

    def start_from_map(
        self,
        iterator: 'Workflow',
        items_path: T.Optional[str] = None,
        max_concurrency: T.Optional[int] = None,
        id: T.Optional[str] = None,
    ) -> 'Workflow':
        """

        """
        map_ = self._map(
            iterator=iterator,
            items_path=items_path,
            max_concurrency=max_concurrency,
            id=id,
        )
        self._start_at = map_.id
        self._add_state(map_)
        self._started = True
        self._previous_state = map_
        return self

    def map(
        self,
        iterator: 'Workflow',
        items_path: T.Optional[str] = None,
        max_concurrency: T.Optional[int] = None,
        id: T.Optional[str] = None,
    ) -> 'Workflow':
        """

        """
        self._check_started()
        map_ = self._map(
            iterator=iterator,
            items_path=items_path,
            max_concurrency=max_concurrency,
            id=id,
        )
        self._previous_state.next = map_.id
        self._add_state(map_)
        self._started = True
        self._previous_state = map_
        return self

    def start_from_choice(
        self,
        choices: T.List['ChoiceRule'],
        default: T.Optional['StateType'] = None,
        id: T.Optional[str] = None
    ):
        """

        """
        choice = self._choice(
            choices=choices,
            default=default,
            id=id,
        )
        self._start_at = choice.id
        self._add_state(choice)
        for choice_rule in choice.choices:
            self._add_state(choice_rule._next_state, ignore_exists=True)
        if default is not None:
            self._add_state(default, ignore_exists=True)
        self._started = True
        self._previous_state = None
        return None

    def choice(
        self,
        choices: T.List['ChoiceRule'],
        default: T.Optional['StateType'] = None,
        id: T.Optional[str] = None
    ):
        """

        """
        self._check_started()
        choice = self._choice(
            choices=choices,
            default=default,
            id=id,
        )
        self._previous_state.next = choice.id
        self._add_state(choice)
        for choice_rule in choice.choices:
            self._add_state(choice_rule._next_state, ignore_exists=True)
        if default is not None:
            self._add_state(default, ignore_exists=True)
        self._started = True
        self._previous_state = None
        return None

    def wait(
        self,
        id: T.Optional[str] = None,
        seconds: T.Optional[int] = None,
        timestamp: T.Optional[str] = None,
        seconds_path: T.Optional[str] = None,
        timestamp_path: T.Optional[str] = None,
    ) -> 'Workflow':
        """
        Create a 'Wait' state and set it as the next.
        """
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
        if self._started is False:
            self.start_from(wait)
        else:
            self._check_started()
            self._previous_state.next = wait.id
            self._add_state(wait)
            self._started = True
            self._previous_state = wait
        return self

    def succeed(
        self,
        id: T.Optional[str] = None,
    ) -> 'Workflow':
        """
        Create a 'Succeed' state and set it as the next.
        """
        kwargs = dict()
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Succeed}-after-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        succeed = Succeed(**kwargs)
        if self._started is False:
            self.start_from(succeed)
        else:
            self._check_started()
            self._previous_state.next = succeed.id
            self._add_state(succeed)
            self._started = True
            self._previous_state = succeed
        return self

    def fail(
        self,
        cause: T.Optional[str] = None,
        error: T.Optional[str] = None,
        id: T.Optional[str] = None,
    ) -> 'Workflow':
        """
        Create a 'Fail' state and set it as the next.
        """
        kwargs = dict(cause=cause, error=error)
        if id is None:
            if self._previous_state is not None:
                kwargs["id"] = f"{C.Fail}-after-{self._previous_state.id}"
        else:
            kwargs["id"] = id
        fail = Fail(**kwargs)
        if self._started is False:
            self.start_from(fail)
        else:
            self._check_started()
            self._previous_state.next = fail.id
            self._add_state(fail)
            self._started = True
            self._previous_state = fail
        return self

    def end(self) -> 'Workflow':
        """
        Mark the workflow is end, and also set the last state in the workflow
        End = True.
        """
        self._previous_state.end = True
        self._started = False
        return self

    def continue_from(self, state: 'StateType') -> 'Workflow':
        """
        Continue workflow from a given state.
        """
        self._add_state(state, ignore_exists=True)
        self._started = True
        self._previous_state = state
        return self

    def _pre_serialize_validation(self):
        if not self._start_at:
            raise exc.WorkflowValidationError.make(
                self,
                f"'StartAt' cannot be empty string!"
            )
        if self._start_at not in self._states:
            raise exc.WorkflowValidationError(
                self,
                f"'StartAt' id {self._start_at!r} is not any of defined State ID"
            )
        # this branch mostly will not hit, just put here for defensive programming
        if len(self._states) == 0:  # pragma: no cover
            raise exc.WorkflowValidationError(
                self,
                "You have to define at least ONE state!"
            )

    def _serialize(self) -> dict:
        # set required fields
        data = {
            C.StartAt: self._start_at,
            C.States: {
                state_id: state.serialize()
                for state_id, state in self._states.items()
            },
        }

        # set optional fields
        if self.comment:
            data[C.Comment] = self.comment
        if self.version:
            data[C.Version] = self.version
        if self.timeout_seconds:
            data[C.TimeoutSeconds] = self.timeout_seconds

        # sort the fields
        data = self._sort_field(data)

        return data
