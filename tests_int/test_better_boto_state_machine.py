# -*- coding: utf-8 -*-

import json

from aws_stepfunction.better_boto.state_machine import (
    StateMachineStatusEnum,
    StateMachineTypeEnum,
    StateMachineLoggingLevelEnum,
    StateMachine,
    create_logging_configuration,
    create_state_machine,
    update_state_machine,
    describe_state_machine,
    delete_state_machine,
    list_state_machines,
    wait_delete_state_machine_to_finish,
)
from aws_stepfunction.tests import (
    run_cov_test,
    bsm,
    aws_console,
)


def test_crud():
    state_name = "Pass"
    definition_data = {
        "Comment": "A description of my state machine",
        "StartAt": state_name,
        "States": {state_name: {"Type": "Pass", "End": True}},
    }
    definition = json.dumps(definition_data)
    state_machine_name = "aws_sfn_better_boto_state_machine_test"
    iam_role = "arn:aws:iam::669508176277:role/sanhe-stepfunc-runner"
    logging_configuration = {
        "level": StateMachineLoggingLevelEnum.ALL.value,
        "includeExecutionData": True,
        "destinations": [
            {
                "cloudWatchLogsLogGroup": {
                    "logGroupArn": f"arn:aws:logs:us-east-1:669508176277:log-group:/aws/vendedlogs/states/{state_machine_name}-Logs:*"
                }
            },
        ],
    }
    print(
        f"preview at: {aws_console.step_function.get_state_machine_view_tab(name_or_arn=state_machine_name)}"
    )

    # --------------------------------------------------------------------------
    # before
    # --------------------------------------------------------------------------
    # delete_state_machine(bsm=bsm, name_or_arn=state_machine_name)
    # wait_delete_state_machine_to_finish(bsm=bsm, name_or_arn=state_machine_name, timeout=60)

    # create
    # create_state_machine(
    #     bsm=bsm,
    #     name=state_machine_name,
    #     definition=definition,
    #     role_arn=iam_role,
    #     logging_configuration=create_logging_configuration(
    #         aws_account_id=bsm.aws_account_id,
    #         aws_region=bsm.aws_region,
    #         state_machine_name=state_machine_name,
    #     ),
    # )

    # describe
    state_machine = describe_state_machine(bsm=bsm, name_or_arn=state_machine_name)
    # print(state_machine)

    # update
    state_name = "Pass1"
    definition_data = {
        "Comment": "A description of my state machine",
        "StartAt": state_name,
        "States": {state_name: {"Type": "Pass", "End": True}},
    }
    definition = json.dumps(definition_data)
    # update_state_machine(
    #     bsm=bsm,
    #     name_or_arn=state_machine_name,
    #     definition=definition,
    # )

    # list
    state_machine_list = list_state_machines(bsm=bsm).filter(lambda state_machine: state_machine.name == state_machine_name).all()
    assert len(state_machine_list) == 1



if __name__ == "__main__":
    run_cov_test(__file__, "aws_stepfunction.better_boto.state_machine", preview=False)
