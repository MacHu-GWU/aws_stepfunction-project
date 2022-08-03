# -*- coding: utf-8 -*-

import os
import pytest
from rich import print as rprint

from aws_stepfunction.statemachine import StateMachine, Task, Parallel
from aws_stepfunction import constant as C


class TestParallel:
    def test_init(self):
        with StateMachine() as sm1:
            task21 = Task(ID="task21", Resource="arn")
            task21.end()
            sm1.set_start_at(task21)

        with StateMachine() as sm2:
            task22 = Task(ID="task22", Resource="arn")
            task22.end()
            sm2.set_start_at(task22)

        para = Parallel(Branches=[sm1, sm2])

        with pytest.raises(Exception):
            para._serialize()

        para.end()
        assert para._serialize() == {
            C.Enum.Type.value: C.Enum.Parallel.value,
            C.Enum.Branches.value: [
                {
                    C.Enum.StartAt.value: task21.ID,
                    C.Enum.States.value: {
                        task21.ID: task21._serialize()
                    }
                },
                {
                    C.Enum.StartAt.value: task22.ID,
                    C.Enum.States.value: {
                        task22.ID: task22._serialize()
                    }
                }
            ],
            C.Enum.End.value: True
        }


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
