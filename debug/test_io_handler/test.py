# -*- coding: utf-8 -*-

from pathlib_mate import Path
from boto_session_manager import BotoSesManager

import aws_stepfunction as sfn
from aws_stepfunction.magic.task import (
    IOHandlerTask,
)

bsm = BotoSesManager(
    profile_name="aws_data_lab_sanhe_us_east_1",
    region_name="us-east-1",
)

workflow = sfn.Workflow()

task1 = sfn.actions.lambda_invoke(
    id="Task1",
    func_name="aws_stepfunction-task1",
    aws_account_id=bsm.aws_account_id,
    aws_region=bsm.aws_region,
)

task1_to_task2 = IOHandlerTask(
    lbd_func_name="aws-stepfunction-io-handler",
    lbd_script=Path("handler.py").absolute().abspath,
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

task2 = sfn.actions.lambda_invoke(
    id="Task2",
    func_name="aws_stepfunction-task2",
    aws_account_id=bsm.aws_account_id,
    aws_region=bsm.aws_region,
)

(
    workflow.start_from(task1)
    .next_then(task1_to_task2)
    .next_then(task2)
    .end()
)

sm_name = "stepfunction_sdk_example1"

state_machine = sfn.StateMachine(
    name=sm_name,
    workflow=workflow,
    role_arn="arn:aws:iam::669508176277:role/sanhe-for-everything-admin",
)

state_machine.deploy(bsm)

result = state_machine.execute(
    bsm,
    payload={"name": "Alice"},
)
