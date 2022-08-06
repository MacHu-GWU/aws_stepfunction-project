# -*- coding: utf-8 -*-

import os
import pytest
from rich import print as rprint

from aws_stepfunction import exc
from aws_stepfunction.constant import Constant as T
from aws_stepfunction.state import (
    Task, Retry, Catch, _RetryOrCatch
)


class TestRetryAndCatch:
    def test_validation(self):
        with pytest.raises(exc.StateValidationError):
            Retry.new()._check_error_codes()

        with pytest.raises(exc.StateValidationError):
            retry = Retry.new()
            retry.error_equals = ["InvalidErrorCode"]
            retry._check_error_codes()

        Retry.new().if_all_error()._check_error_codes()

    def test_add_error(self):
        retry = Retry.new()
        for attribute in _RetryOrCatch.__dict__:
            if attribute.startswith("if_"):
                getattr(retry, attribute)()

    def test_serialize(self):
        # Retry
        retry = (
            Retry.new()
            .with_interval_seconds(10)
            .with_back_off_rate(2.0)
            .with_max_attempts(3)
            .if_lambda_service_error()
            .if_lambda_aws_error()
            .if_lambda_sdk_client_error()
            .if_lambda_too_many_requests_error()
        )
        assert retry.serialize() == {
            T.ErrorEquals: [
                T.LambdaServiceError,
                T.LambdaAWSError,
                T.LambdaSdkClientError,
                T.LambdaTooManyRequestsError,
            ],
            T.IntervalSeconds: 10,
            T.BackoffRate: 2.0,
            T.MaxAttempts: 3,
        }

        # Catch
        task = Task(id="last")
        catch = (
            Catch.new()
            .with_result_path("$.result")
            .next_then(task)
            .if_lambda_unknown_error()
        )
        assert catch.serialize() == {
            T.ErrorEquals: [
                T.LambdaUnknownError,
            ],
            T.ResultPath: "$.result",
            T.Next: task.id,
        }


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
