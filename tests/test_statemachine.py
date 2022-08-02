# -*- coding: utf-8 -*-

import os
import pytest
from aws_stepfunction.statemachine import _context, StateMachine


class TestContext:
    def test(self):
        assert len(_context.envs) == 0
        with StateMachine(
            ID="abc",
            Comment="First State Machine",
        ) as sm:
            assert sm.ID in _context.envs


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
