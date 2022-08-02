# -*- coding: utf-8 -*-

import os
import pytest
from aws_stepfunction.statemachine import _context, StateMachine


class TestContext:
    def test(self):
        assert len(_context.queue) == 0
        with StateMachine(
            ID="abc",
            Comment="First State Machine",
        ) as sm1:
            assert len(_context.queue) == 1
            assert _context.queue[-1].ID == sm1.ID

            with StateMachine(
                ID="xyz",
                Comment="Second State Machine",
            ) as sm2:
                assert len(_context.queue) == 2
                assert _context.queue[-1].ID == sm2.ID

            assert len(_context.queue) == 1
            assert _context.queue[-1].ID == sm1.ID

        assert len(_context.queue) == 0


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
