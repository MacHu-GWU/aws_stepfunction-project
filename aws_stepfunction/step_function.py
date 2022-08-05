# -*- coding: utf-8 -*-

import typing as T
import json

import attr

from .model import StepFunctionObject

if T.TYPE_CHECKING:
    from .state_machine import StateMachine
    from boto_session_manager import BotoSesManager, AwsServiceEnum


@attr.s
class StepFunction(StepFunctionObject):
    aws_account_id: str = attr.ib()
    aws_region: str = attr.ib()
    name: str = attr.ib()
    state_machine: 'StateMachine' = attr.ib()
    type: str = attr.ib()
    role_arn: str = attr.ib()
    logging_configuration: dict = attr.ib()
    tags: dict = attr.ib()
    tracing_configuration: dict = attr.ib()

    def create(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.create_state_machine
        """
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        return sfn_client.create_state_machine(
            name=self.name,
            definition=json.dumps(self.state_machine.serialize()),
            roleArn=self.role_arn,
            type=self.type,
            loggingConfiguration=self.logging_configuration,
            tags=self.tags,
            tracingConfiguration=self.tracing_configuration,
        )

    def update(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.update_state_machine
        """

    def delete(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.delete_state_machine
        """

    def execute(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.start_execution
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.start_sync_execution
        """
