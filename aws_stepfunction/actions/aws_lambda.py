# -*- coding: utf-8 -*-

"""

"""

import typing as T
from .base import TaskResource, TaskMaker, Task, Retry, _resolve_resource_arn


def lambda_invoke(
    func_name: str,
    sync: T.Optional[bool] = True,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> 'Task':
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.lambda_invoke_wait_for_callback
    else:
        resource = TaskResource.lambda_invoke
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        output_path="$.Payload",
        parameters={
            "Payload.$": "$",
            "FunctionName": _resolve_resource_arn(
                resource_name=func_name,
                resource_type="lambda",
                path="",
                aws_account_id=aws_account_id,
                aws_region=aws_region,
            ),
        },
        retry=[
            (
                Retry.new()
                .with_interval_seconds(2)
                .with_back_off_rate(2)
                .with_max_attempts(3)
                .if_lambda_service_error()
                .if_lambda_aws_error()
                .if_lambda_sdk_client_error()
            )
        ],
    )
    if sync is False:
        task_maker.parameters["InvocationType"] = "Event"
    return task_maker.make()
