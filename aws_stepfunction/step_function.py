# -*- coding: utf-8 -*-

import typing as T
import json

import attr
from boto_session_manager import BotoSesManager, AwsServiceEnum

from .model import StepFunctionObject
from .constant import Constant as C
from .logger import logger

if T.TYPE_CHECKING:
    from .state_machine import StateMachine


@attr.s
class StepFunction(StepFunctionObject):
    name: str = attr.ib()
    state_machine: 'StateMachine' = attr.ib()
    role_arn: str = attr.ib(
        metadata={C.ALIAS: "roleArn"},
    )
    type: T.Optional[str] = attr.ib(default="STANDARD")
    logging_configuration: T.Optional[dict] = attr.ib(
        default=None, metadata={C.ALIAS: "loggingConfiguration"},
    )
    tags: T.Optional[dict] = attr.ib(default=None)
    tracing_configuration: T.Optional[dict] = attr.ib(
        default=None, metadata={C.ALIAS: "tracingConfiguration"},
    )

    # aws_account_id: str = attr.ib()
    # aws_region: str = attr.ib()

    def get_state_machine_arn(self, bsm: 'BotoSesManager') -> str:
        return (
            f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
            f"stateMachine:{self.name}"
        )

    def get_state_machine_console_url(self, bsm: 'BotoSesManager') -> str:
        return (
            f"https://{bsm.aws_region}.console.aws.amazon.com/states/"
            f"home?region={bsm.aws_region}#/statemachines/view/"
            f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
            f"stateMachine:{self.name}"
        )

    def get_state_machine_visual_editor_console_url(self, bsm: 'BotoSesManager') -> str:
        return (
            f"https://{bsm.aws_region}.console.aws.amazon.com/states/"
            f"home?region={bsm.aws_region}#/visual-editor?stateMachineArn="
            f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
            f"stateMachine:{self.name}"
        )

    def describe(self, bsm: 'BotoSesManager'):
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        return sfn_client.describe_state_machine(
            stateMachineArn=self.get_state_machine_arn(bsm)
        )

    def exists(self, bsm: 'BotoSesManager') -> bool:
        try:
            self.describe(bsm)
            return True
        except Exception as e:
            if "StateMachineDoesNotExist" in e.__class__.__name__:
                return False
            else:
                raise e

    def create(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.create_state_machine
        """
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        kwargs = self.to_dict()
        kwargs = self._to_alias(kwargs)
        kwargs.pop("state_machine")
        kwargs["definition"] = json.dumps(self.state_machine.serialize())
        return sfn_client.create_state_machine(**kwargs)

    def update(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.update_state_machine
        """
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        kwargs = self.to_dict()
        kwargs = self._to_alias(kwargs)
        kwargs["stateMachineArn"] = f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:stateMachine:{self.name}"
        kwargs.pop("name")
        kwargs.pop("type")
        kwargs.pop("state_machine")
        kwargs["definition"] = json.dumps(self.state_machine.serialize())
        return sfn_client.update_state_machine(**kwargs)

    def delete(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.delete_state_machine
        """
        state_machine_arn = self.get_state_machine_arn(bsm)
        logger.info(f"delete state machine {state_machine_arn!r}")
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        res = sfn_client.delete_state_machine(stateMachineArn=state_machine_arn)
        logger.info(f"  done, exam at: {self.get_state_machine_console_url(bsm)}")
        return res

    def execute(
        self,
        bsm: 'BotoSesManager',
        name: T.Optional[str] = None,
        payload: T.Optional[dict] = None,
        sync: bool = False,
        trace_header: T.Optional[str] = None,
    ):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.start_execution
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.start_sync_execution
        """
        state_machine_arn = self.get_state_machine_arn(bsm)
        logger.info(f"execute state machine {state_machine_arn!r}")
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        kwargs = dict(stateMachineArn=state_machine_arn)
        if name is not None:
            kwargs["name"] = name
        if payload is not None:
            kwargs["input"] = json.dumps(payload)
        if trace_header is not None:
            kwargs["traceHeader"] = trace_header
        if sync:
            res = sfn_client.start_sync_execution(**kwargs)
        else:
            res = sfn_client.start_execution(**kwargs)
        execution_arn = res["executionArn"]
        execution_id = execution_arn.split(":")[-1]
        execution_console_url = (
            f"https://{bsm.aws_region}.console.aws.amazon.com/states/"
            f"home?region={bsm.aws_region}#/executions/details/"
            f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
            f"execution:{self.name}:{execution_id}"
        )
        logger.info(f"  preview at: {execution_console_url}")
        return res

    def deploy(self, bsm: 'BotoSesManager') -> dict:
        logger.info(
            f"deploy state machine to {self.get_state_machine_arn(bsm)!r} ..."
        )
        if self.exists(bsm):
            logger.info("  already exists, update state machine ...")
            res = self.update(bsm)
            logger.info(f"  done, preview at: {self.get_state_machine_visual_editor_console_url(bsm)}")
            res["_deploy_action"] = "update"
        else:
            logger.info("  not exists, create state machine ...")
            res = self.create(bsm)
            res["_deploy_action"] = "create"
            logger.info(f"  done, preview at: {self.get_state_machine_visual_editor_console_url(bsm)}")
        return res
