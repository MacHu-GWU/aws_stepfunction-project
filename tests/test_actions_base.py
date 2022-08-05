# -*- coding: utf-8 -*-

import os
import pytest

from rich import print as rprint
from aws_stepfunction.actions.base import (
    _TaskContext, task_context,
    _resolve_lambda_function_arn,
    lambda_invoke,
)


@pytest.fixture
def set_task_context():
    task_context.aws_account_id = "111122223333"
    task_context.aws_region = "us-east-1"


def test_resolve_lambda_function_arn():
    with pytest.raises(ValueError):
        _resolve_lambda_function_arn(func_name="hello")

    task_context.aws_account_id = "111122223333"
    task_context.aws_region = "us-east-1"
    arn = _resolve_lambda_function_arn(func_name="hello")
    assert arn == "arn:aws:lambda:us-east-1:111122223333:hello"


def test_lambda_invoke(set_task_context):
    lambda_invoke_hello = lambda_invoke(func_name="hello", sync=False).update(end=True)
    lambda_invoke_hello.serialize()

    # rprint(lambda_invoke_hello)
    # rprint(lambda_invoke_hello.serialize())



if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
