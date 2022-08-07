# -*- coding: utf-8 -*-

import os
import pytest

from aws_stepfunction.actions.base import (
    task_context,
    _resolve_resource_arn,
)


@pytest.fixture
def set_task_context():
    task_context.aws_account_id = "111122223333"
    task_context.aws_region = "us-east-1"


def test_resolve_resource_arn():
    with pytest.raises(ValueError):
        _resolve_resource_arn(resource_name="hello", resource_type="lambda", path="")

    task_context.aws_account_id = "111122223333"
    task_context.aws_region = "us-east-1"
    arn = _resolve_resource_arn(resource_name="hello", resource_type="lambda", path="")
    assert arn == "arn:aws:lambda:us-east-1:111122223333:hello"


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
