# -*- coding: utf-8 -*-

"""

"""

import typing as T

import attr
import attr.validators as vs

from . import exc
from .constant import Constant as C, TestExpressionEnum
from .utils import is_json_path
from .model import StepFunctionObject

if T.TYPE_CHECKING: # pragma: no cover
    from .state import StateType

# ------------------------------------------------------------------------------
# Choice Rule
# ------------------------------------------------------------------------------
__a_1_choice_rule = None


@attr.s
class ChoiceRule(StepFunctionObject):
    """
    Reference:

    - https://states-language.net/spec.html#choice-state, search keyword
        "Choice Rule"
    - https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-choice-state.html#amazon-states-language-choice-state-rules
    """
    next: T.Optional[str] = attr.ib(
        default=None,
        validator=vs.optional(vs.instance_of(str)),
        metadata={C.ALIAS: C.Next},
    )

    _next_state: T.Optional['StateType'] = attr.ib(default=None)

    def next_then(self, state: 'StateType'):
        if self._next_state is None:
            self.next = state.id
            self._next_state = state
            return self
        else:
            raise exc.WorkflowError(
                f"A 'ChoiceRule' can only call 'next_then' method once! "
                "To continue workflow from the existing 'next' state "
                f"{self._next_state._short_repr()}, "
                f"use 'workflow.continue_from({self._next_state._short_repr()})"
                f".next_then({state._short_repr()})' to continue orchestration."
            )

    def _check_next(self):
        if self.next is None:
            raise exc.ValidationError(
                f"Top level choice rule has to have a {C.Next!r} state"
            )


# ------------------------------------------------------------------------------
# Data test expression
# ------------------------------------------------------------------------------
__a_2_data_test_expression = None


def _is_json_path(inst, attr, value):
    if not is_json_path(value):
        raise exc.ValidationError


@attr.s
class DataTestExpression(ChoiceRule):
    """
    Compare object is a data container to hold the logic of:

    "Check if 'value' match 'expected' in certain way"

    There are three type of compare:

    1. Compare a 'value' to another given raw value.
    2. Compare a 'value' to a value at specific JSON path.
    3. If a 'value' is certain data type or if it presents.

    Reference:

    - https://states-language.net/spec.html#choice-state
    - https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-choice-state.html#amazon-states-language-choice-state-rules
    """
    variable: str = attr.ib(
        default="",
        validator=[vs.instance_of(str), _is_json_path],
    )
    operator: str = attr.ib(default="")
    expected: T.Union[str, T.Any] = attr.ib(default="")
    next: T.Optional[str] = attr.ib(
        default=None,
        validator=vs.optional(vs.instance_of(str)),
    )

    @operator.validator
    def check_operator(self, attribute, value):
        if not TestExpressionEnum.contains(self.operator):
            raise exc.ValidationError

    def _check_expected(self):
        if self.operator.endswith("Path"):
            if not is_json_path(self.expected):
                raise exc.ValidationError

    def _pre_serialize_validation(self):
        self._check_expected()

    def _serialize(self) -> dict:
        data = {C.Variable: self.variable, self.operator: self.expected}
        if self.next:
            data[C.Next] = self.next
        return data


@attr.s
class Var(StepFunctionObject):
    path: str = attr.ib(validator=vs.instance_of(str))

    def is_null(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsNull,
            expected=True,
        )

    def is_not_null(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsNull,
            expected=False,
        )

    def is_present(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsPresent,
            expected=True,
        )

    def is_not_present(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsPresent,
            expected=False,
        )

    def is_numeric(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsNumeric,
            expected=True,
        )

    def is_not_numeric(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsNumeric,
            expected=False,
        )

    def is_string(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsString,
            expected=True,
        )

    def is_not_string(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsString,
            expected=False,
        )

    def is_boolean(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsBoolean,
            expected=True,
        )

    def is_not_boolean(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsBoolean,
            expected=False,
        )

    def is_timestamp(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsTimestamp,
            expected=True,
        )

    def is_not_timestamp(self) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.IsTimestamp,
            expected=False,
        )

    def numeric_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.NumericEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.NumericEquals,
            expected=value,
        )

    def numeric_greater_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.NumericGreaterThanPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.NumericGreaterThan,
            expected=value,
        )

    def numeric_greater_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.NumericGreaterThanEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.NumericGreaterThanEquals,
            expected=value,
        )

    def numeric_less_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.NumericLessThanPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.NumericLessThan,
            expected=value,
        )

    def numeric_less_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.NumericLessThanEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.NumericLessThanEquals,
            expected=value,
        )

    def string_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.StringEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.StringEquals,
            expected=value,
        )

    def string_greater_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.StringGreaterThanPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.StringGreaterThan,
            expected=value,
        )

    def string_greater_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.StringGreaterThanEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.StringGreaterThanEquals,
            expected=value,
        )

    def string_less_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.StringLessThanPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.StringLessThan,
            expected=value,
        )

    def string_less_than_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.StringLessThanEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.StringLessThanEquals,
            expected=value,
        )

    def boolean_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.BooleanEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.BooleanEquals,
            expected=value,
        )

    def timestamp_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.TimestampEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.TimestampEquals,
            expected=value,
        )

    def timestamp_greater_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.TimestampGreaterThanPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.TimestampGreaterThan,
            expected=value,
        )

    def timestamp_greater_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.TimestampGreaterThanEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.TimestampGreaterThanEquals,
            expected=value,
        )

    def timestamp_less_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.TimestampLessThanPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.TimestampLessThan,
            expected=value,
        )

    def timestamp_less_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$"):
                return DataTestExpression(
                    variable=self.path,
                    operator=C.TimestampLessThanEqualsPath,
                    expected=value,
                )
        return DataTestExpression(
            variable=self.path,
            operator=C.TimestampLessThanEquals,
            expected=value,
        )

    def string_matches(self, value: str) -> DataTestExpression:
        return DataTestExpression(
            variable=self.path,
            operator=C.StringMatches,
            expected=value,
        )


Test = DataTestExpression  # alias of DataTestExpression

# ------------------------------------------------------------------------------
# Boolean expression
# ------------------------------------------------------------------------------
__a_3_boolean_expression = None


@attr.s
class BooleanExpression(ChoiceRule):
    pass


@attr.s
class And(BooleanExpression):
    rules: T.List['ChoiceRule'] = attr.ib(factory=list)

    _field_order = [
        C.And,
        C.Next,
    ]

    def _serialize(self) -> dict:
        data = {C.And: [rule.serialize() for rule in self.rules]}
        if self.next:
            data[C.Next] = self.next
        return data


@attr.s
class Or(BooleanExpression):
    rules: T.List['ChoiceRule'] = attr.ib(factory=list)

    _field_order = [
        C.Or,
        C.Next,
    ]

    def _serialize(self) -> dict:
        data = {C.Or: [rule.serialize() for rule in self.rules]}
        if self.next:
            data[C.Next] = self.next
        return data


@attr.s
class Not(BooleanExpression):
    rule: T.Optional['ChoiceRule'] = attr.ib(default=None)

    _field_order = [
        C.Not,
        C.Next,
    ]

    def _serialize(self) -> dict:
        data = {C.Not: self.rule.serialize()}
        if self.next:
            data[C.Next] = self.next
        return data


def and_(*rules: 'ChoiceRule') -> And:
    return And(rules=list(rules))


def or_(*rules: 'ChoiceRule') -> Or:
    return Or(rules=list(rules))


def not_(rule: 'ChoiceRule') -> Not:
    return Not(rule=rule)


Bool = BooleanExpression  # alias of BooleanExpression
