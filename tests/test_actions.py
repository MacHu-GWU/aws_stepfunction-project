# -*- coding: utf-8 -*-

import os
import pytest

from aws_stepfunction.actions.base import task_context
from aws_stepfunction.actions import lambda_invoke


@pytest.fixture
def set_task_context():
    task_context.aws_account_id = "111122223333"
    task_context.aws_region = "us-east-1"


def test_lambda_invoke(set_task_context):
    lambda_invoke_hello = lambda_invoke(func_name="hello", sync=False).update(end=True)
    lambda_invoke_hello.serialize()


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
