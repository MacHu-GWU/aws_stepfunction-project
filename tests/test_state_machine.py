# -*- coding: utf-8 -*-

import os
import pytest

from rich import print as rprint

from aws_stepfunction import exc
from aws_stepfunction.state_machine import StateMachine
from aws_stepfunction.state import Task, Succeed, Fail
from aws_stepfunction.choice_rule import Var


class TestStateMachine:
    def test_workflow(self):
        sm = StateMachine()

        t01 = Task(id="T01", resource="arn")
        t02 = Task(id="T02", resource="arn")
        t03_a1 = Task(id="T03-a1", resource="arn")
        t03_a2 = Task(id="T03-a2", resource="arn")
        t03_b1 = Task(id="T03-b1", resource="arn")
        t03_b2 = Task(id="T03-b2", resource="arn")
        t03_c = Task(id="T03-c", resource="arn")
        t03_c_succeed = Succeed()
        t03_c_fail = Fail()
        t04 = Task(id="T04", resource="arn")
        t05_a1 = Task(id="T05-a1", resource="arn")
        t05_a2 = Task(id="T05-a2", resource="arn")
        t05_b1 = Task(id="T05-b1", resource="arn")
        t05_b2 = Task(id="T05-b2", resource="arn")
        t06 = Task(id="T06", resource="arn")
        t07 = Task(id="T07", resource="arn")
        t08 = Task(id="T08", resource="arn")
        t09 = Task(id="T09", resource="arn")
        t10 = Task(id="T10", resource="arn")

        (
            sm.start(t01)
            .next_then(t02)
            .choice([
                (
                    Var("$.key").string_equals("v1").next_then(t03_a1)
                ),
                (
                    Var("$.key").string_equals("v2").next_then(t03_b1)
                ),
                (
                    Var("$.key").string_equals("v3").next_then(t03_c)
                ),
            ])
            .default_fail()
        )

        (
            sm.continue_from(t03_a1)
            .next_then(t03_a2)
            .next_then(t04)
        )

        (
            sm.continue_from(t03_b1)
            .next_then(t03_b2)
            .next_then(t04)
        )

        (
            sm.continue_from(t03_c)
            .choice([
                Var("$.flag").boolean_equals(True).next_then(t03_c_succeed),
                Var("$.flag").boolean_equals(False).next_then(t03_c_fail),
            ])
        )

        (
            sm.continue_from(t04)
            .parallel(
                branches=[
                    (
                        sm.parallel_from(t05_a1)
                        .next_then(t05_a2)
                        .end()
                    ),
                    (
                        sm.parallel_from(t05_b1)
                        .next_then(t05_b2)
                        .end()
                    ),
                ]
            )
            .next_then(t06)
            .wait()
            .next_then(t07)
            .map(
                iterator=(
                    sm.map_from(t08)
                    .next_then(t09)
                    .end()
                ),
                items_path="$.items",
            )
            .next_then(t10)
            .end()
        )
        # rprint(sm._previous_state)
        # rprint(sm.serialize())


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
