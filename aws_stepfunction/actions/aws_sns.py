# -*- coding: utf-8 -*-

"""

"""

import typing as T
from .base import TaskResource, TaskMaker, Task, _resolve_resource_arn


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
        resource = TaskResource.sns_publish_wait_for_callback
    else:
        resource = TaskResource.sns_publish
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "TopicArn": _resolve_resource_arn(
                resource_name=topic,
                resource_type="sns",
                path="",
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


def sns_publish_batch(
    topic: str,
    message_list: T.List[dict],
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> Task:
    """
    :param message_list: example,
        ``[{"Id": "MyData", "Message", "MyData"}, ...]``
    """
    if wait_for_call_back is True:
        resource = TaskResource.sns_publish_batch_wait_for_callback
    else:
        resource = TaskResource.sns_publish_batch
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "TopicArn": _resolve_resource_arn(
                resource_name=topic,
                resource_type="sns",
                path="",
                aws_account_id=aws_account_id,
                aws_region=aws_region,
            ),
            "PublishBatchRequestEntries": message_list,
        },
    )
    return task_maker.make()
