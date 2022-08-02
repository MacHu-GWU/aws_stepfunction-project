# -*- coding: utf-8 -*-

import os
import pytest
from aws_stepfunction.statemachine import StateMachine, Task


def test():
    with StateMachine() as sm:
        task = Task()



if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
