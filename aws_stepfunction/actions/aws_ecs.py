# -*- coding: utf-8 -*-

"""

"""

import typing as T
from .base import TaskResource, TaskMaker, Task, _resolve_resource_arn


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
        resource = TaskResource.ecs_run_task_wait_for_callback
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
            "TaskDefinition": _resolve_resource_arn(
                resource_name=task_def,
                resource_type="ecs",
                path="task-definition/",
                aws_account_id=aws_account_id,
                aws_region=aws_region,
            ),
        },
    )
    return task_maker.make()


def ecs_start_task(
    task_def: str,
    container_instances: T.List[str],
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
    aws_account_id: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> 'Task':
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.ecs_start_task_wait_for_callback
    else:
        resource = TaskResource.ecs_start_task
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "ContainerInstances": container_instances,
            "TaskDefinition": _resolve_resource_arn(
                resource_name=task_def,
                resource_type="ecs",
                path="task-definition/",
                aws_account_id=aws_account_id,
                aws_region=aws_region,
            ),
        },
    )
    return task_maker.make()


def ecs_stop_task(
    task: str,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
) -> 'Task':
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.ecs_stop_task_wait_for_callback
    else:
        resource = TaskResource.ecs_stop_task
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "Task": task,
        },
    )
    return task_maker.make()
