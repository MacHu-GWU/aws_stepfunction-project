# -*- coding: utf-8 -*-

import os
import pytest

from rich import print as rprint

from aws_stepfunction.state import Retry, Catch, Task, Fail
from aws_stepfunction.constant import Constant as C
from aws_stepfunction import exc


class TestTask:
    def test_init(self):
        task = Task(id="task", resource="arn")

        with pytest.raises(exc.StateValidationError):
            task._pre_serialize_validation()

        task.end = True
        assert task.serialize() == {
            C.Type: C.Task,
            C.Resource: "arn",
            C.End: True
        }

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
                Retry().if_all_error().with_max_attempts(1).with_interval_seconds(10),
                Retry().if_task_failed_error().with_max_attempts(1).with_interval_seconds(10),
            ],
            catch=[
                Catch().if_all_error().next_then(fail),
            ],
            end=True,
        )
        _ = task.serialize()
        # rprint(task.serialize())


if __name__ == "__main__":
    import sys
    import subprocess

    abspath = os.path.abspath(__file__)
    dir_project_root = os.path.dirname(abspath)
    for _ in range(10):
        if os.path.exists(os.path.join(dir_project_root, ".git")):
            break
        else:
            dir_project_root = os.path.dirname(dir_project_root)
    else:
        raise FileNotFoundError("cannot find project root dir!")
    dir_htmlcov = os.path.join(dir_project_root, "htmlcov")
    bin_pytest = os.path.join(os.path.dirname(sys.executable), "pytest")

    args = [
        bin_pytest,
        "-s", "--tb=native",
        f"--rootdir={dir_project_root}",
        "--cov=aws_stepfunction.state",
        "--cov-report", "term-missing",
        "--cov-report", f"html:{dir_htmlcov}",
        abspath,
    ]
    subprocess.run(args)
