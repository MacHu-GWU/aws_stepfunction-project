# -*- coding: utf-8 -*-

import os
import pytest
from rich import print as rprint
from aws_stepfunction.state_machine import StateMachine
from aws_stepfunction.state import (
    State, Task, Parallel, Map, Pass, Wait, Choice, Succeed, Fail
)


class TestState:
    @pytest.mark.parametrize(
        "klass",
        [
            Task, Parallel, Map, Pass, Wait, Choice, Succeed, Fail,
        ],
    )
    def test_invalid_state_id(self, klass: State):
        with pytest.raises(Exception):
            klass(id=1)


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
