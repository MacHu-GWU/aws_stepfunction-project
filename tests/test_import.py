# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx


def test():
    import aws_stepfunction

    _ = aws_stepfunction.Workflow

    _ = aws_stepfunction.State
    _ = aws_stepfunction.Task
    _ = aws_stepfunction.Parallel
    _ = aws_stepfunction.Map
    _ = aws_stepfunction.Pass
    _ = aws_stepfunction.Wait
    _ = aws_stepfunction.Choice
    _ = aws_stepfunction.Succeed
    _ = aws_stepfunction.Fail
    _ = aws_stepfunction.Retry
    _ = aws_stepfunction.Catch

    _ = aws_stepfunction.LambdaTask

    _ = aws_stepfunction.ChoiceRule
    _ = aws_stepfunction.and_
    _ = aws_stepfunction.or_
    _ = aws_stepfunction.not_
    _ = aws_stepfunction.Var

    _ = aws_stepfunction.actions
    _ = aws_stepfunction.task_context
    _ = aws_stepfunction.StateMachine
    _ = aws_stepfunction.Constant

    _ = aws_stepfunction.better_boto.StateMachineStatusEnum
    _ = aws_stepfunction.better_boto.StateMachineTypeEnum
    _ = aws_stepfunction.better_boto.StateMachineLoggingLevelEnum
    _ = aws_stepfunction.better_boto.StateMachine
    _ = aws_stepfunction.better_boto.create_logging_configuration
    _ = aws_stepfunction.better_boto.create_state_machine
    _ = aws_stepfunction.better_boto.update_state_machine
    _ = aws_stepfunction.better_boto.describe_state_machine
    _ = aws_stepfunction.better_boto.delete_state_machine
    _ = aws_stepfunction.better_boto.StateMachineIterProxy
    _ = aws_stepfunction.better_boto.list_state_machines
    _ = aws_stepfunction.better_boto.wait_delete_state_machine_to_finish
    _ = aws_stepfunction.better_boto.to_tag_list
    _ = aws_stepfunction.better_boto.to_tag_dict
    _ = aws_stepfunction.better_boto.WaiterError
    _ = aws_stepfunction.better_boto.Waiter


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
