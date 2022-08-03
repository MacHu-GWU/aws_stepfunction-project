# -*- coding: utf-8 -*-

import os
import pytest
from aws_stepfunction.statemachine import _context, StateMachine


class TestContext:
    def test(self):
        # at begin we got nothing in context queue
        assert len(_context.stack) == 0
        with StateMachine(
            ID="sm1",
            Comment="First State Machine",
        ) as sm1:
            assert len(_context.stack) == 1
            assert _context.current.ID == sm1.ID

            with StateMachine(
                ID="sm2",
                Comment="Second State Machine",
            ) as sm2:
                assert len(_context.stack) == 2
                assert _context.current.ID == sm2.ID

            assert len(_context.stack) == 1
            assert _context.current.ID == sm1.ID

            with StateMachine(
                ID="sm3",
                Comment="Third State Machine",
            ) as sm3:
                assert len(_context.stack) == 2
                assert _context.current.ID == sm3.ID

            assert len(_context.stack) == 1
            assert _context.current.ID == sm1.ID

        assert len(_context.stack) == 0


class TestStateMachine:
    def test_pre_serialize_validations(self):
        with pytest.raises(Exception):
            sm = StateMachine()
            sm.serialize()

        with pytest.raises(Exception):
            sm = StateMachine(StartAt="void")
            sm.serialize()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
