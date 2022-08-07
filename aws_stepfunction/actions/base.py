# -*- coding: utf-8 -*-

"""

"""

import typing as T
import attr
from ..state import Task, Retry, Catch


@attr.s
class _TaskContext:
    aws_account_id: T.Optional[str] = attr.ib(default=None)
    aws_region: T.Optional[str] = attr.ib(default=None)

    def reset(self):
        self.aws_account_id = None
        self.aws_region = None

    def _resolve_value(self, attr: str, value: T.Optional[str]) -> str:
        if (value is None) and (getattr(self, attr) is None):
            raise ValueError(
                f"{attr!r} is not defined!"
            )
        elif value is not None:
            return value
        else:
            return getattr(self, attr)

    def _resolve_aws_account_id(self, aws_account_id: T.Optional[str]) -> str:
        return self._resolve_value("aws_account_id", aws_account_id)

    def _resolve_aws_region(self, aws_region: T.Optional[str]) -> str:
        return self._resolve_value("aws_region", aws_region)


task_context = _TaskContext()


@attr.s
class TaskMaker:
    id: T.Optional[str] = attr.ib(default=None)
    resource: T.Optional[str] = attr.ib(default=None)
    timeout_seconds_path: T.Optional[str] = attr.ib(default=None)
    timeout_seconds: T.Optional[int] = attr.ib(default=None)
    heartbeat_seconds_path: T.Optional[str] = attr.ib(default=None)
    heartbeat_seconds: T.Optional[int] = attr.ib(default=None)
    next: T.Optional[str] = attr.ib(default=None)
    end: T.Optional[bool] = attr.ib(default=None)
    input_path: T.Optional[str] = attr.ib(default=None)
    output_path: T.Optional[str] = attr.ib(default=None)
    parameters: T.Dict[str, T.Any] = attr.ib(factory=dict)
    result_selector: T.Dict[str, T.Any] = attr.ib(factory=dict)
    result_path: T.Optional[str] = attr.ib(default=None)
    retry: T.List['Retry'] = attr.ib(factory=list)
    catch: T.List['Catch'] = attr.ib(factory=list)

    def make(self) -> 'Task':
        data = {
            k: v
            for k, v in attr.asdict(self, recurse=False).items()
            if v
        }
        return Task(**data)


# ------------------------------------------------------------------------------
# AWS Lambda
# ------------------------------------------------------------------------------
__TASK_RESOURCE = None


class TaskResource:
    lambda_invoke = "arn:aws:states:::lambda:invoke"
    lambda_invoke_wait_for_callback = "arn:aws:states:::lambda:invoke.waitForTaskToken"

    ecs_run_task = "arn:aws:states:::ecs:runTask.sync"
    ecs_run_task_async = "arn:aws:states:::ecs:runTask"
    ecs_run_task_wait_for_callback = "arn:aws:states:::ecs:runTask.waitForTaskToken"
    ecs_start_task = "arn:aws:states:::aws-sdk:ecs:startTask.waitForTaskToken"
    ecs_start_task_wait_for_callback = "arn:aws:states:::aws-sdk:ecs:startTask.waitForTaskToken"
    ecs_stop_task = "arn:aws:states:::aws-sdk:ecs:stopTask"
    ecs_stop_task_wait_for_callback = "arn:aws:states:::aws-sdk:ecs:stopTask"

    glue_start_job_run = "arn:aws:states:::glue:startJobRun.sync"
    glue_start_job_run_async = "arn:aws:states:::glue:startJobRun"
    glue_batch_stop_job_run = "arn:aws:states:::aws-sdk:glue:batchStopJobRun"
    glue_batch_stop_job_run_wait_for_callback = "arn:aws:states:::aws-sdk:glue:batchStopJobRun.waitForTaskToken"
    glue_start_crawler = "arn:aws:states:::aws-sdk:glue:startCrawler"
    glue_start_crawler_wait_for_callback = "arn:aws:states:::aws-sdk:glue:startCrawler.waitForTaskToken"
    glue_stop_crawler = "arn:aws:states:::aws-sdk:glue:stopCrawler"
    glue_stop_crawler_wait_for_callback = "arn:aws:states:::aws-sdk:glue:stopCrawler.waitForTaskToken"

    sns_publish = "arn:aws:states:::sns:publish"
    sns_publish_wait_for_callback = "arn:aws:states:::sns:publish.waitForTaskToken"
    sns_publish_batch = "arn:aws:states:::aws-sdk:sns:publishBatch"
    sns_publish_batch_wait_for_callback = "arn:aws:states:::aws-sdk:sns:publishBatch.waitForTaskToken"

    sqs_send_message = "arn:aws:states:::sqs:sendMessage"
    sqs_send_message_wait_for_callback = "arn:aws:states:::sqs:sendMessage.waitForTaskToken"
    sqs_send_message_batch = "arn:aws:states:::sqs:sendMessageBatch"
    sqs_send_message_batch_wait_for_callback = "arn:aws:states:::sqs:sendMessageBatch.waitForTaskToken"

    batch_submit_job = "arn:aws:states:::batch:submitJob.sync"
    batch_cancel_job = "arn:aws:states:::aws-sdk:batch:cancelJob"
    batch_cancel_job_wait_for_callback = "arn:aws:states:::aws-sdk:batch:cancelJob.waitForTaskToken"
    batch_terminate_job = "arn:aws:states:::aws-sdk:batch:terminateJob"
    batch_terminate_job_wait_for_callback = "arn:aws:states:::aws-sdk:batch:terminateJob.waitForTaskToken"


def _resolve_resource_arn(
    resource_name: str,
    resource_type: str,
    path: str,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> str:
    if resource_name.startswith(f"arn:aws:{resource_type}:"):
        return resource_name
    aws_account_id = task_context._resolve_aws_account_id(aws_account_id)
    aws_region = task_context._resolve_aws_region(aws_region)
    return f"arn:aws:{resource_type}:{aws_region}:{aws_account_id}:{path}{resource_name}"
