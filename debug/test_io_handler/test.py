# -*- coding: utf-8 -*-

import json
import aws_stepfunction as sfn
from aws_stepfunction.magic import LambdaTask

from boto_session_manager import BotoSesManager
from rich import print as rprint

bsm = BotoSesManager(
    profile_name="aws_data_lab_sanhe_us_east_1",
    region_name="us-east-1",
)

workflow = sfn.Workflow()

task1_get_order_detail = LambdaTask(
    id="Task1-Get-Order-Detail",
    lbd_func_name="aws_stepfunction_magic_task_demo-task1_get_order_detail",
    lbd_package="s1_get_order_detail.py",
    lbd_handler="s1_get_order_detail.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

task2a_1_extract_items = LambdaTask(
    id="Task2a-1-Extract-Items",
    lbd_func_name="aws_stepfunction_magic_task_demo-task2a_1_extract_items",
    lbd_package="s2a_1_extract_items.py",
    lbd_handler="s2a_1_extract_items.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

task2a_2_get_item_cost = LambdaTask(
    id="Task2a-2-Get-Item-Cost",
    lbd_func_name="aws_stepfunction_magic_task_demo-task2a_2_get_item_cost",
    lbd_package="s2a_2_get_item_cost.py",
    lbd_handler="s2a_2_get_item_cost.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

task2b_1_extract_ship_address = LambdaTask(
    id="Task2b-1-Extract-Ship-Address",
    lbd_func_name="aws_stepfunction_magic_task_demo-task2b_1_extract_ship_address",
    lbd_package="s2b_1_extract_ship_address.py",
    lbd_handler="s2b_1_extract_ship_address.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

task2b_2_get_ship_cost = LambdaTask(
    id="Task2b-2-Get-Ship-Cost",
    lbd_func_name="aws_stepfunction_magic_task_demo-task2b_2_get_ship_cost",
    lbd_package="s2b_2_get_ship_cost.py",
    lbd_handler="s2b_2_get_ship_cost.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

task3_find_balance = LambdaTask(
    id="Task3-Find-Balance",
    lbd_func_name="aws_stepfunction_magic_task_demo-task3_find_balance",
    lbd_package="s3_find_balance.py",
    lbd_handler="s3_find_balance.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

task4_process_payment = LambdaTask(
    id="Task4-Process-Payment",
    lbd_func_name="aws_stepfunction_magic_task_demo-task4_process_payment",
    lbd_package="s4_process_payment.py",
    lbd_handler="s4_process_payment.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

(
    workflow.start_from(task1_get_order_detail)
    .parallel([
        (
            workflow.subflow_from(task2a_1_extract_items)
            .next_then(task2a_2_get_item_cost)
            .end()
        ),
        (
            workflow.subflow_from(task2b_1_extract_ship_address)
            .next_then(task2b_2_get_ship_cost)
            .end()
        ),
    ])
    .next_then(task3_find_balance)
    .next_then(task4_process_payment)
    .end()
)

# rprint(workflow.serialize())

sfn_name = "aws_stepfunction_magic_task_demo"

state_machine = sfn.StateMachine(
    name=sfn_name,
    workflow=workflow,
    role_arn="arn:aws:iam::669508176277:role/sanhe-for-everything-admin",
)
state_machine.set_type_as_express()

deploy_result = state_machine.deploy(bsm, verbose=True)

execute_result = state_machine.execute(
    bsm,
    payload={"order_id": "order-1"},
    sync=True,
)

input = json.loads(execute_result["input"])
output = json.loads(execute_result["output"])
print(f"\ninput:\n")
print(json.dumps(input))
print(f"\noutput:\n")
print(json.dumps(output))

result = state_machine.execute(
    bsm,
    payload={"order_id": "order-1"},
)

#------------------------------------------------------------------------------
# Clean up
#------------------------------------------------------------------------------
