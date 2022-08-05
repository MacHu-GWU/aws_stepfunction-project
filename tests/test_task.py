# -*- coding: utf-8 -*-

import os
import pytest
from rich import print as rprint
from aws_stepfunction.state import Retry, Catch, Task, Fail
from aws_stepfunction.constant import Constant as C
from aws_stepfunction import exc


class TestTask:
    # def test_init(self):
    #     task = Task(id="task", resource="arn")
    #
    #     with pytest.raises(exc.StateValidationError):
    #         task._pre_serialize_validation()
    #
    #     task.end = True
    #     assert task.serialize() == {
    #         C.Type: C.Task,
    #         C.Resource: "arn",
    #         C.End: True
    #     }

    def test_input_output(self):
        fail = Fail()
        task = Task(
            id="task",
            resource="arn",
            input_path="$.key_in",
            parameters={
                "key_in": "$.key_in"
            },
            result_selector={
                "key_out": "$.key_out"
            },
            result_path="$.task_result",
            output_path="$.key_out",
            retry=[
                Retry().at_all_error().with_max_attempts(1).with_interval_seconds(10),
                Retry().at_task_failed_error().with_max_attempts(1).with_interval_seconds(10),
            ],
            catch=[
                Catch().at_all_error().next_then(fail),
            ],
            end=True,
        )
        rprint(task.serialize())


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
