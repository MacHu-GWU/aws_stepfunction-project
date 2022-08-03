# -*- coding: utf-8 -*-

import os
import pytest
from rich import print as rprint
from aws_stepfunction.statemachine import Task
from aws_stepfunction import constant as C


class TestTask:
    def test_init(self):
        task = Task(ID="task", Resource="arn")

        with pytest.raises(Exception):
            task.pre_serialize_validation()

        task.end()
        assert task._serialize() == {
            C.Enum.Type.value: C.Enum.Task.value,
            C.Enum.Resource.value: "arn",
            C.Enum.End.value: True
        }


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
