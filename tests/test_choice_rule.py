# -*- coding: utf-8 -*-

import os
import pytest

from rich import print as rprint

from aws_stepfunction import exc
from aws_stepfunction import choice_rule as CR
from aws_stepfunction.constant import Constant as C
from aws_stepfunction.state import Task


class TestLogicOperator:
    def test_constructor(self):
        # data expression
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
        task = Task(id="last")

        and_rule.next_then(task)
        assert C.Next in and_rule.serialize()

        or_rule.next_then(task)
        assert C.Next in or_rule.serialize()

        not_rule.next_then(task)
        assert C.Next in not_rule.serialize()


class TestDataTestExpression:
    def test(self):
        var = CR.Var("$.key")
        cr = var.is_present()
        cr.next = "last"
        cr.serialize()

        # invalid variable
        with pytest.raises(exc.ValidationError):
            _ = CR.DataTestExpression(variable="")

        # invalid operator
        with pytest.raises(exc.ValidationError):
            _ = CR.DataTestExpression(variable="$", operator="")

        # invalid expected
        with pytest.raises(exc.ValidationError):
            cr = CR.DataTestExpression(
                variable="$", operator=C.StringEqualsPath, expected=""
            )
            cr._check_expected()


    def test_condition(self):
        var = CR.Var("$.key")
        for k in CR.Var.__dict__:
            if (
                k.startswith("is_")
            ):
                getattr(var, k)()

            if (
                "_equals" in k
                or "_greater_than" in k
                or "_less_than" in k
                or k == "string_matches"
            ):
                getattr(var, k)(1)
                getattr(var, k)("$.")


if __name__ == "__main__":
    import sys
    import subprocess

    abspath = os.path.abspath(__file__)
    dir_project_root = os.path.dirname(abspath)
    for _ in range(10):
        if os.path.exists(os.path.join(dir_project_root, ".git")):
            break
        else:
            dir_project_root = os.path.dirname(dir_project_root)
    else:
        raise FileNotFoundError("cannot find project root dir!")
    dir_htmlcov = os.path.join(dir_project_root, "htmlcov")
    bin_pytest = os.path.join(os.path.dirname(sys.executable), "pytest")

    args = [
        bin_pytest,
        "-s", "--tb=native",
        f"--rootdir={dir_project_root}",
        "--cov=aws_stepfunction.choice_rule",
        "--cov-report", "term-missing",
        "--cov-report", f"html:{dir_htmlcov}",
        abspath,
    ]
    subprocess.run(args)