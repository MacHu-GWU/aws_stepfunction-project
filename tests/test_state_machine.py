# -*- coding: utf-8 -*-

import os
import pytest

from rich import print as rprint

from aws_stepfunction import exc
from aws_stepfunction.state_machine import _context, StateMachine
from aws_stepfunction.state import Task
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
            .next(t02)
            .choice([
                (
                    Var("$.key").string_equals("v1")
                    # .next(t03_a1)
                    # .next(t03_a2)
                    # .next(t04)
                ),
                # (
                #     Var("$.key").string_equals("v2")
                #     .next(t03_b1)
                #     .next(t03_b2)
                #     .next(t04)
                # ),
                # (
                #     Var("$.key").string_equals("v2")
                #     .next(t03_b1)
                #     .next(t03_b2)
                #     .next(t04)
                # )
            ])
            # .default_fail()
            .end()
        )
        #
        # (
        #     sm.continue_from(t04)
        #     .parallel([
        #         t05_a1.next(t05_a2).end(),
        #         t05_b1.next(t05_b2).end(),
        #     ])
        #     .next(t06)
        #     .wait(
        #         seconds=10,
        #     )
        #     .next(t07)
        #     .map(
        #         t08.next(t09),
        #         items_path="$.items",
        #     )
        #     .next(t10)
        #     .end()
        # )

        rprint(sm.serialize())

# class TestContext:
#     def test(self):
#         # at begin we got nothing in context queue
#         assert len(_context.stack) == 0
#         with StateMachine(
#             ID="sm1",
#             Comment="First State Machine",
#         ) as sm1:
#             assert len(_context.stack) == 1
#             assert _context.current.ID == sm1.ID
#
#             with StateMachine(
#                 ID="sm2",
#                 Comment="Second State Machine",
#             ) as sm2:
#                 assert len(_context.stack) == 2
#                 assert _context.current.ID == sm2.ID
#
#             assert len(_context.stack) == 1
#             assert _context.current.ID == sm1.ID
#
#             with StateMachine(
#                 ID="sm3",
#                 Comment="Third State Machine",
#             ) as sm3:
#                 assert len(_context.stack) == 2
#                 assert _context.current.ID == sm3.ID
#
#             assert len(_context.stack) == 1
#             assert _context.current.ID == sm1.ID
#
#         assert len(_context.stack) == 0
#
#
# class TestStateMachine:
#     def test_pre_serialize_validations(self):
#         with pytest.raises(exc.StateMachineValidationError):
#             sm = StateMachine()
#             sm.serialize()
#
#         with pytest.raises(exc.StateMachineValidationError):
#             sm = StateMachine(StartAt="void")
#             sm.serialize()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
