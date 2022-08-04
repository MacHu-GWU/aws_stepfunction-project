# -*- coding: utf-8 -*-

import os
import pytest
from rich import print as rprint
from aws_stepfunction.state import Retry, Catch, Task
from aws_stepfunction.constant import Constant as C
from aws_stepfunction import exc


class TestTask:
    def test_init(self):
        task = Task(ID="task", Resource="arn")

        with pytest.raises(exc.StateValidationError):
            task._pre_serialize_validation()

        task.end()
        assert task.serialize() == {
            C.Type: C.Task,
            C.Resource: "arn",
            C.End: True
        }

    def test_input_output(self):
        task = Task(
            ID="task",
            Resource="arn",
            InputPath="$.key_in",
            Parameters={
                "key_in": "$.key_in"
            },
            ResultSelector={
                "key_out": "$.key_out"
            },
            ResultPath="$.task_result",
            OutputPath="$.key_out",
            Retry=[
                Retry().at_all_error().with_max_attempts(1).with_interval_seconds(10),
                Retry().at_task_failed_error().with_max_attempts(1).with_interval_seconds(10),
            ],
            Catch=[
                Catch().at_all_error()
            ],
            End=True,
        )
        rprint(task.serialize())


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
