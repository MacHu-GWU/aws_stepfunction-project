# -*- coding: utf-8 -*-

"""

"""

import typing as T
from .base import TaskResource, TaskMaker, Task, _resolve_resource_arn


def batch_submit_job(
    job_name: str,
    job_definition: str,
    job_queue: str,
    id: T.Optional[str] = None,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> 'Task':
    """
    """
    task_maker = TaskMaker(
        id=id,
        resource=TaskResource.batch_submit_job,
        parameters={
            "JobName": job_name,
            "JobDefinition": _resolve_resource_arn(
                resource_name=job_definition,
                resource_type="batch",
                path="job-definition/",
                aws_account_id=aws_account_id,
                aws_region=aws_region,
            ),
            "JobQueue": _resolve_resource_arn(
                resource_name=job_queue,
                resource_type="batch",
                path="job-queue/",
                aws_account_id=aws_account_id,
                aws_region=aws_region,
            ),
        },
    )
    return task_maker.make()


def batch_cancel_job(
    job_id: str,
    reason: str,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
) -> 'Task':
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.batch_cancel_job_wait_for_callback
    else:
        resource = TaskResource.batch_cancel_job
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        output_path="$.Payload",
        parameters={
            "JobId": job_id,
            "Reason": reason,
        },
    )
    return task_maker.make()


def batch_terminate_job(
    job_id: str,
    reason: str,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
) -> 'Task':
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.batch_terminate_job_wait_for_callback
    else:
        resource = TaskResource.batch_terminate_job
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        output_path="$.Payload",
        parameters={
            "JobId": job_id,
            "Reason": reason,
        },
    )
    return task_maker.make()
