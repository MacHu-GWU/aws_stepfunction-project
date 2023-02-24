# -*- coding: utf-8 -*-

import typing as T
import enum
import dataclasses
from datetime import datetime

from iterproxy import IterProxy
from func_args import NOTHING, resolve_kwargs
from boto_session_manager import BotoSesManager

from .waiter import WaiterError, Waiter
from .tagging import to_tag_list

# ------------------------------------------------------------------------------
# Data Model
# ------------------------------------------------------------------------------
class StateMachineStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"


class StateMachineTypeEnum(str, enum.Enum):
    STANDARD = "STANDARD"
    EXPRESS = "EXPRESS"


class StateMachineLoggingLevelEnum(str, enum.Enum):
    ALL = "ALL"
    ERROR = "ERROR"
    FATAL = "FATAL"
    OFF = "OFF"


def _ensure_state_machine_arn(bsm: BotoSesManager, name_or_arn: str) -> str:
    if name_or_arn.startswith("arn:"):
        return name_or_arn
    else:
        return StateMachine.build_arn(
            aws_account_id=bsm.aws_account_id,
            aws_region=bsm.aws_region,
            name=name_or_arn,
        )


@dataclasses.dataclass
class StateMachine:
    name: T.Optional[str] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)
    definition: T.Optional[str] = dataclasses.field(default=None)
    type: T.Optional[str] = dataclasses.field(default=None)
    create_time: T.Optional[datetime] = dataclasses.field(default=None)
    status: T.Optional[str] = dataclasses.field(default=None)
    role_arn: T.Optional[str] = dataclasses.field(default=None)
    logging_configuration: T.Optional[dict] = dataclasses.field(default_factory=dict)
    tracing_configuration: T.Optional[dict] = dataclasses.field(default_factory=dict)
    label: T.Optional[str] = dataclasses.field(default=None)

    @property
    def logging_level(self) -> str:
        return self.logging_configuration["level"]

    @classmethod
    def from_describe_state_machine_response(cls, response: dict) -> "StateMachine":
        return cls(
            name=response["name"],
            arn=response["stateMachineArn"],
            definition=response["definition"],
            type=response["type"],
            create_time=response["creationDate"],
            status=response["status"],
            role_arn=response["roleArn"],
            logging_configuration=response.get("loggingConfiguration", {}),
            tracing_configuration=response.get("tracingConfiguration", {}),
            label=response.get("label"),
        )

    @classmethod
    def build_arn(
        cls,
        aws_account_id: str,
        aws_region: str,
        name: str,
    ) -> str:
        return f"arn:aws:states:{aws_region}:{aws_account_id}:stateMachine:{name}"

    def refresh(self) -> "StateMachine":
        pass


# ------------------------------------------------------------------------------
# Boto3
# ------------------------------------------------------------------------------
def create_log_group(
    bsm: BotoSesManager,
    log_group_name: str,
):
    response = bsm.logs_client.describe_log_groups(
        logGroupNamePrefix=log_group_name,
    )
    if len(response["logGroups"]) == 0:
        bsm.logs_client.create_log_group(
            logGroupName=log_group_name,
        )


def create_logging_configuration(
    aws_account_id: str,
    aws_region: str,
    state_machine_name: str,
    level: str = StateMachineLoggingLevelEnum.ALL.value,
    include_execution_data: bool = True,
    log_group_arn: str = NOTHING,
) -> dict:
    logging_configuration = {
        "level": level,
        "includeExecutionData": include_execution_data,
    }
    if level != StateMachineLoggingLevelEnum.OFF.value:  # has to define destination
        if log_group_arn is NOTHING:
            log_group_arn = (
                f"arn:aws:logs:{aws_region}:{aws_account_id}:log-group:"
                f"/aws/vendedlogs/states/{state_machine_name}-Logs:*"
            )
        logging_configuration["destinations"] = [
            {
                "cloudWatchLogsLogGroup": {
                    "logGroupArn": log_group_arn,
                }
            },
        ]
    return logging_configuration


def create_state_machine(
    bsm: BotoSesManager,
    name: str,
    definition: str,
    role_arn: str,
    type: str = StateMachineTypeEnum.STANDARD.value,
    logging_configuration: dict = NOTHING,
    tracing_configuration: dict = NOTHING,
    tags: T.Dict[str, str] = NOTHING,
) -> dict:
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.create_state_machine
    """
    if logging_configuration is not NOTHING:
        logging_level = logging_configuration["level"]
        if (
            logging_level != StateMachineLoggingLevelEnum.OFF.value
        ):  # has to define destination
            log_group_arn = logging_configuration["destinations"][0][
                "cloudWatchLogsLogGroup"
            ]["logGroupArn"]
            log_group_name = log_group_arn.split(":")[-2]
            create_log_group(bsm=bsm, log_group_name=log_group_name)

    if tags is not NOTHING:
        tags = to_tag_list(tags)

    return bsm.stepfunctions_client.create_state_machine(
        **resolve_kwargs(
            name=name,
            definition=definition,
            roleArn=role_arn,
            type=type,
            loggingConfiguration=logging_configuration,
            tracingConfiguration=tracing_configuration,
            tags=tags,
        )
    )


def update_state_machine(
    bsm: BotoSesManager,
    name_or_arn: str,
    definition: str = NOTHING,
    role_arn: str = NOTHING,
    logging_configuration: dict = NOTHING,
    tracing_configuration: dict = NOTHING,
) -> dict:
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.update_state_machine
    """
    arn = _ensure_state_machine_arn(bsm=bsm, name_or_arn=name_or_arn)
    return bsm.stepfunctions_client.update_state_machine(
        **resolve_kwargs(
            stateMachineArn=arn,
            definition=definition,
            roleArn=role_arn,
            loggingConfiguration=logging_configuration,
            tracingConfiguration=tracing_configuration,
        )
    )


def describe_state_machine(
    bsm: BotoSesManager,
    name_or_arn: str,
) -> T.Optional[StateMachine]:
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.describe_state_machine
    """
    arn = _ensure_state_machine_arn(bsm=bsm, name_or_arn=name_or_arn)
    try:
        response = bsm.stepfunctions_client.describe_state_machine(
            stateMachineArn=arn,
        )
        return StateMachine.from_describe_state_machine_response(response=response)
    except Exception as e:
        if "StateMachineDoesNotExist" in str(e):
            return None
        else:
            raise e


def delete_state_machine(
    bsm: BotoSesManager,
    name_or_arn: str,
) -> bool:
    """
    :return: a boolean flag that indicates whether a deletion happened or not.
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.delete_state_machine
    """
    arn = _ensure_state_machine_arn(bsm=bsm, name_or_arn=name_or_arn)
    state_machine = describe_state_machine(bsm=bsm, name_or_arn=arn)
    if state_machine is None:
        return False
    bsm.stepfunctions_client.delete_state_machine(stateMachineArn=arn)
    return True


def _list_state_machines(
    bsm: BotoSesManager,
    max_items: int = 1000,
    page_size: int = 100,
) -> T.Iterable[StateMachine]:
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.list_state_machines
    """
    paginator = bsm.stepfunctions_client.get_paginator("list_state_machines")
    response_iterator = paginator.paginate(
        PaginationConfig={
            "MaxItems": max_items,
            "PageSize": page_size,
        }
    )
    for response in response_iterator:
        for state_machine_data in response["stateMachines"]:
            yield StateMachine(
                name=state_machine_data["name"],
                arn=state_machine_data["stateMachineArn"],
                type=state_machine_data["type"],
                create_time=state_machine_data["creationDate"],
            )


class StateMachineIterProxy(IterProxy[StateMachine]):
    pass


def list_state_machines(
    bsm: BotoSesManager,
    max_items: int = 1000,
    page_size: int = 100,
) -> StateMachineIterProxy:
    return StateMachineIterProxy(
        _list_state_machines(bsm=bsm, max_items=max_items, page_size=page_size)
    )


def wait_delete_state_machine_to_finish(
    bsm: BotoSesManager,
    name_or_arn: str,
    delays: int = 5,
    timeout: int = 60,
    verbose: bool = True,
):
    arn = _ensure_state_machine_arn(bsm=bsm, name_or_arn=name_or_arn)
    if verbose:  # pragma: no cover
        print(f"wait for delete state machine {arn} to finish ...")
    succeeded_status = []
    failed_status = []
    for _ in Waiter(delays=delays, timeout=timeout, verbose=verbose):
        state_machine = describe_state_machine(bsm=bsm, name_or_arn=arn)
        if state_machine is None:
            if verbose:
                print(f"endpoint doesn't exists.")
            return False
        status = state_machine.status
        if status in [
            StateMachineStatusEnum.ACTIVE.value,
        ]:
            raise WaiterError(f"failed with status {status!r}")
        else:
            pass
    if verbose:  # pragma: no cover
        print(f"state machine is deleted.")
