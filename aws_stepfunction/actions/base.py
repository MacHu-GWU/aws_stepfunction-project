# -*- coding: utf-8 -*-

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
    lambda_invoke_wait_for_call_back = "arn:aws:states:::lambda:invoke.waitForTaskToken"

    ecs_run_task = "arn:aws:states:::ecs:runTask.sync"
    ecs_run_task_async = "arn:aws:states:::ecs:runTask"
    ecs_run_task_wait_for_call_back = "arn:aws:states:::ecs:runTask.waitForTaskToken"

    glue_start_job_run = "arn:aws:states:::glue:startJobRun.sync"
    glue_start_job_run_async = "arn:aws:states:::glue:startJobRun"

    sns_publish = "arn:aws:states:::sns:publish"
    sns_publish_wait_for_call_back = "arn:aws:states:::sns:publish.waitForTaskToken"


# ------------------------------------------------------------------------------
# AWS Lambda Task
# ------------------------------------------------------------------------------
__AWS_LAMBDA_TASK = None


def _resolve_lambda_function_arn(
    func_name: str,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> str:
    if func_name.startswith("arn:aws:lambda:"):
        return func_name
    aws_account_id = task_context._resolve_aws_account_id(aws_account_id)
    aws_region = task_context._resolve_aws_region(aws_region)
    return f"arn:aws:lambda:{aws_region}:{aws_account_id}:{func_name}"


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
        resource = TaskResource.lambda_invoke_wait_for_call_back
    else:
        resource = TaskResource.lambda_invoke
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        output_path="$.Payload",
        parameters={
            "Payload.$": "$",
            "FunctionName": _resolve_lambda_function_arn(
                func_name=func_name,
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


# ------------------------------------------------------------------------------
# AWS ECS Task
# ------------------------------------------------------------------------------
__AWS_ECS_TASK = None


def _resolve_ecs_task_def_arn(
    task_def: str,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> str:
    if task_def.startswith("arn:aws:ecs:"):
        return task_def
    aws_account_id = task_context._resolve_aws_account_id(aws_account_id)
    aws_region = task_context._resolve_aws_region(aws_region)
    return f"arn:aws:ecs:{aws_region}:{aws_account_id}:task-definition/{task_def}"


def ecs_run_task(
    task_def: str,
    sync: T.Optional[bool] = True,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> Task:
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.ecs_run_task_wait_for_call_back
    elif sync:
        resource = TaskResource.ecs_run_task
    else:
        resource = TaskResource.ecs_run_task_async
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "LaunchType": "FARGATE",
            "Cluster": "arn:aws:ecs:REGION:ACCOUNT_ID:cluster/MyECSCluster",
            "TaskDefinition": _resolve_ecs_task_def_arn(
                task_def=task_def,
                aws_account_id=aws_account_id,
                aws_region=aws_region,
            ),
        },
    )
    return task_maker.make()


# ------------------------------------------------------------------------------
# AWS Glue Task
# ------------------------------------------------------------------------------
__AWS_GLUE_TASK = None


def glue_start_job_run(
    job_name: str,
    sync: T.Optional[bool] = True,
    id: T.Optional[str] = None,
) -> Task:
    """
    """
    if sync:
        resource = TaskResource.glue_start_job_run
    else:
        resource = TaskResource.glue_start_job_run_async
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "JobName": job_name,
        },
    )
    return task_maker.make()


# ------------------------------------------------------------------------------
# AWS SNS Task
# ------------------------------------------------------------------------------
__AWS_SNS_TASK = None


def _resolve_sns_topic_arn(
    topic: str,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> str:
    if topic.startswith("arn:aws:sns:"):
        return topic
    aws_account_id = task_context._resolve_aws_account_id(aws_account_id)
    aws_region = task_context._resolve_aws_region(aws_region)
    return f"arn:aws:sns:{aws_region}:{aws_account_id}:{topic}"


def sns_publish(
    topic: str,
    message: T.Optional[dict] = None,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> Task:
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.sns_publish_wait_for_call_back
    else:
        resource = TaskResource.sns_publish
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "TopicArn": _resolve_sns_topic_arn(
                topic=topic,
                aws_account_id=aws_account_id,
                aws_region=aws_region,
            )
        },
    )
    if message is None:
        task_maker.parameters["Message.$"] = "$"
    else:
        task_maker.parameters["Message"] = message
    return task_maker.make()
