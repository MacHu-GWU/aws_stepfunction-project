# -*- coding: utf-8 -*-

"""

"""

import typing as T
from .base import TaskResource, TaskMaker, Task, _resolve_resource_arn


def sqs_send_message(
    queue_url: str,
    message: T.Optional[dict] = None,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
) -> Task:
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.sqs_send_message_wait_for_callback
    else:
        resource = TaskResource.sqs_send_message
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "QueueUrl": queue_url,
        },
    )
    if message is None:
        task_maker.parameters["MessageBody.$"] = "$"
    else:
        task_maker.parameters["MessageBody"] = message
    return task_maker.make()


def sqs_send_message_batch(
    queue_url: str,
    message_list: T.Optional[dict],
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
) -> Task:
    """
    :param message_list: example,
        ``[{"Id": "MyData", "MessageBody", "MyData"}, ...]``
    """
    if wait_for_call_back is True:
        resource = TaskResource.sqs_send_message_batch_wait_for_callback
    else:
        resource = TaskResource.sqs_send_message_batch
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "QueueUrl": queue_url,
            "Entries": message_list,
        },
    )
    return task_maker.make()
