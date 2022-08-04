# -*- coding: utf-8 -*-

import os
import pytest

from rich import print as rprint
from aws_stepfunction import choice_rule as CR
from aws_stepfunction.constant import Constant as C
from aws_stepfunction.state import Task

class TestLogicOperator:
    def test(self):
        rule = CR.Var("$.key").is_present()
        rule_data = {C.Variable: "$.key", C.IsPresent: True}

        # Basic
        # and
        and_rule = CR.and_(rule, rule)
        and_rule_data = {
            C.And: [rule_data, rule_data]
        }
        assert and_rule.serialize() == and_rule_data

        # or
        or_rule = CR.or_(rule, rule)
        or_rule_data = {
            C.Or: [rule_data, rule_data]
        }
        assert or_rule.serialize() == or_rule_data

        # not
        not_rule = CR.not_(rule)
        not_rule_data = {
            C.Not: rule_data,
        }
        assert not_rule.serialize() == not_rule_data

        # Compound
        bool_expr = CR.and_(
            rule,
            and_rule,
            or_rule,
            not_rule,
        )
        assert bool_expr.serialize() == {
            C.And: [
                rule_data,
                and_rule_data,
                or_rule_data,
                not_rule_data,
            ]
        }

        bool_expr = CR.or_(
            rule,
            and_rule,
            or_rule,
            not_rule,
        )
        assert bool_expr.serialize() == {
            C.Or: [
                rule_data,
                and_rule_data,
                or_rule_data,
                not_rule_data,
            ]
        }

        bool_expr = CR.not_(
            and_rule,
        )
        assert bool_expr.serialize() == {
            C.Not: and_rule_data
        }

        # next
        task = Task(ID="last task")

        and_rule.next(task)
        assert C.Next in and_rule.serialize()

        or_rule.next(task)
        assert C.Next in or_rule.serialize()

        not_rule.next(task)
        assert C.Next in not_rule.serialize()


class TestDataTestExpression:
    def test(self):
        var = CR.Var("$.key")
        var.is_present().serialize()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
