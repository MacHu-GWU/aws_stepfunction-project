# -*- coding: utf-8 -*-

import os
import pytest
from rich import print as rprint

from aws_stepfunction.constant import Constant as T
from aws_stepfunction.state import (
    Task, Retry, Catch,
)


class TestRetryAndCatch:
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
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
