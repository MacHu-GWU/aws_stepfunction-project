# -*- coding: utf-8 -*-

import typing as T

import attr
import attr.validators as vs

from .constant import Constant as C, TestExpressionEnum
from .utils import is_json_path
from .model import StepFunctionObject


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
    """

    Next: T.Optional[str] = attr.ib(
        default=None, validator=vs.optional(vs.instance_of(str))
    )

    def next(self, state: str) -> "ChoiceRule":
        self.Next = state
        return self


# ------------------------------------------------------------------------------
# Data test expression
# ------------------------------------------------------------------------------
__a_2_data_test_expression = None


def _is_json_path(inst, attr, value):
    if not is_json_path(value):
        raise ValueError


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
    """

    Variable: str = attr.ib(
        default="",
        validator=[vs.instance_of(str), _is_json_path],
    )
    Operator: str = attr.ib(default="")
    Expected: T.Union[str, T.Any] = attr.ib(default="")
    Next: T.Optional[str] = attr.ib(
        default=None,
        validator=vs.optional(vs.instance_of(str)),
    )

    @Operator.validator
    def check_operator(self, attribute, value):
        if self.Operator not in TestExpressionEnum._value2member_map_:
            raise ValueError

    def _pre_serialize_validation(self):
        if self.Operator.endswith("Path"):
            if not is_json_path(self.Expected):
                raise ValueError

    def _serialize(self) -> dict:
        data = {C.Variable: self.Variable, self.Operator: self.Expected}
        if self.Next:
            data[C.Next] = self.Next
        return data


@attr.s
class Var(StepFunctionObject):
    path: str = attr.ib(validator=vs.instance_of(str))

    def is_null(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsNull, True)

    def is_not_null(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsNull, False)

    def is_present(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsPresent, True)

    def is_not_present(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsPresent, False)

    def is_numeric(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsNumeric, True)

    def is_not_numeric(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsNumeric, False)

    def is_string(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsString, True)

    def is_not_string(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsString, False)

    def is_boolean(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsBoolean, True)

    def is_not_boolean(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsBoolean, False)

    def is_timestamp(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsTimestamp, True)

    def is_not_timestamp(self) -> DataTestExpression:
        return DataTestExpression(self.path, C.IsTimestamp, False)

    def numeric_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.NumericEqualsPath, value
                )
        return DataTestExpression(self.path, C.NumericEquals, value)

    def numeric_greater_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.NumericGreaterThanPath, value
                )
        return DataTestExpression(self.path, C.NumericGreaterThan, value)

    def numeric_greater_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.NumericGreaterThanEqualsPath, value
                )
        return DataTestExpression(
            self.path, C.NumericGreaterThanEquals, value
        )

    def numeric_less_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.NumericLessThanPath, value
                )
        return DataTestExpression(self.path, C.NumericLessThan, value)

    def numeric_less_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.NumericLessThanEqualsPath, value
                )
        return DataTestExpression(self.path, C.NumericLessThanEquals, value)

    def string_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.StringEqualsPath, value
                )
        return DataTestExpression(self.path, C.StringEquals, value)

    def string_greater_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.StringGreaterThanPath, value
                )
        return DataTestExpression(self.path, C.StringGreaterThan, value)

    def string_greater_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.StringGreaterThanEqualsPath, value
                )
        return DataTestExpression(
            self.path, C.StringGreaterThanEquals, value
        )

    def string_less_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.StringLessThanPath, value
                )
        return DataTestExpression(self.path, C.StringLessThan, value)

    def string_less_than_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.StringLessThanEqualsPath, value
                )
        return DataTestExpression(self.path, C.StringLessThanEquals, value)

    def boolean_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.BooleanEqualsPath, value
                )
        return DataTestExpression(self.path, C.BooleanEquals, value)

    def timestamp_equals(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.TimestampEqualsPath, value
                )
        return DataTestExpression(self.path, C.TimestampEquals, value)

    def timestamp_greater_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.TimestampGreaterThanPath, value
                )
        return DataTestExpression(self.path, C.TimestampGreaterThan, value)

    def timestamp_greater_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.TimestampGreaterThanEqualsPath, value
                )
        return DataTestExpression(
            self.path, C.TimestampGreaterThanEquals, value
        )

    def timestamp_less_than(self, value: T.Union[str, T.Any]) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.TimestampLessThanPath, value
                )
        return DataTestExpression(self.path, C.TimestampLessThan, value)

    def timestamp_less_than_equals(
        self, value: T.Union[str, T.Any]
    ) -> DataTestExpression:
        if isinstance(value, str):
            if value.startswith("$."):
                return DataTestExpression(
                    self.path, C.TimestampLessThanEqualsPath, value
                )
        return DataTestExpression(
            self.path, C.TimestampLessThanEquals, value
        )

    def string_matches(self, value: str) -> DataTestExpression:
        return DataTestExpression(self.path, C.StringMatches, value)


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
    Rules: T.List["ChoiceRule"] = attr.ib(factory=list)

    _se_order = [
        C.And,
        C.Next,
    ]

    def _serialize(self) -> dict:
        data = {C.And: [rule.serialize() for rule in self.Rules]}
        if self.Next:
            data[C.Next] = self.Next
        return data


@attr.s
class Or(BooleanExpression):
    Rules: T.List["ChoiceRule"] = attr.ib(factory=list)

    _se_order = [
        C.Or,
        C.Next,
    ]

    def _serialize(self) -> dict:
        data = {C.Or: [rule.serialize() for rule in self.Rules]}
        if self.Next:
            data[C.Next] = self.Next
        return data


@attr.s
class Not(BooleanExpression):
    Rule: T.Optional["ChoiceRule"] = attr.ib(default=None)

    _se_order = [
        C.Not,
        C.Next,
    ]

    def _serialize(self) -> dict:
        data = {C.Not: self.Rule.serialize()}
        if self.Next:
            data[C.Next] = self.Next
        return data


def and_(*rules: "ChoiceRule") -> And:
    return And(Rules=list(rules))


def or_(*rules: "ChoiceRule") -> Or:
    return Or(Rules=list(rules))


def not_(rule: "ChoiceRule") -> Not:
    return Not(Rule=rule)


Bool = BooleanExpression  # alias of BooleanExpression
