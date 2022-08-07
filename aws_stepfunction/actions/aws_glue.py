# -*- coding: utf-8 -*-

"""

"""

import typing as T
from .base import TaskResource, TaskMaker, Task, _resolve_resource_arn


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


def glue_batch_stop_job_run(
    job_name: str,
    job_run_id_list: T.List[str],
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
) -> Task:
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.glue_batch_stop_job_run_wait_for_callback
    else:
        resource = TaskResource.glue_batch_stop_job_run
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "JobName": job_name,
            "JobRunIds": job_run_id_list,
        },
    )
    return task_maker.make()


def glue_start_crawler(
    crawler_name: str,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
) -> Task:
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.glue_start_crawler_wait_for_callback
    else:
        resource = TaskResource.glue_start_crawler
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "Name": crawler_name
        },
    )
    return task_maker.make()


def glue_stop_crawler(
    crawler_name: str,
    wait_for_call_back: T.Optional[bool] = False,
    id: T.Optional[str] = None,
) -> Task:
    """
    """
    if wait_for_call_back is True:
        resource = TaskResource.glue_stop_crawler_wait_for_callback
    else:
        resource = TaskResource.glue_stop_crawler
    task_maker = TaskMaker(
        id=id,
        resource=resource,
        parameters={
            "Name": crawler_name
        },
    )
    return task_maker.make()
