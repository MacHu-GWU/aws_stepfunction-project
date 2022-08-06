# -*- coding: utf-8 -*-

"""
This is a minimal usage of `aws_stepfunction <https://pypi.org/project/aws-stepfunction/>`_
library.

.. code-block:: python

    # content of lambda_handler.py

    import json
    import random

    def lambda_handler(event, context):
        if random.randint(1, 100) <= 70:
            return {
                "statusCode": 200,
                "body": json.dumps(event),
            }
        else:
            return {
                "statusCode": 400,
                "body": "failed!"
            }
"""

# ------------------------------------------------------------------------------
# Step 1. import, preparation
# ------------------------------------------------------------------------------\
# Import the "aws_stepfunction" library,
# all public API can be accessed from the "sfn" namespace
import aws_stepfunction as sfn
from boto_session_manager import BotoSesManager

# Create a boto3 session manager object
# the credential you are using should have STS.get_caller_identity permission
# it is for getting the AWS Account ID information
bsm = BotoSesManager(
    profile_name="aws_data_lab_sanhe_us_east_1",
    region_name="us-east-1",
)

# You could tell the task context about the aws_account_id and aws_region
# then you can only need to provide lambda function name without the full ARN.
sfn.task_context.aws_account_id = bsm.aws_account_id
sfn.task_context.aws_region = bsm.aws_region

# Declare a state machine object
workflow = sfn.Workflow(
    comment="The power of aws_stepfunction library!",  # put random comment here
)

# ------------------------------------------------------------------------------
# Step 2. Define some tasks and states
# ------------------------------------------------------------------------------
# There are some helper functions to create common task.
# These helper functions are just the equivalent of
# The widget in Step Function Visual Editor

# define a lambda function invoke task
task_invoke_lambda = sfn.actions.lambda_invoke(func_name="stepfunction_quick_start")

# define a succeed state
succeed = sfn.Succeed()

# define a fail state
fail = sfn.Fail()

# ------------------------------------------------------------------------------
# Step 3. Orchestrate the Workflow
# ------------------------------------------------------------------------------
# We use this "Human-language alike", "Pythonic", "Objective Oriented"
# "Auto-complete empowered" code pattern to create a human-readable workflow
(
    workflow.start_from(task_invoke_lambda)
    .choice([
        # choice 1, succeed case
        (  # define condition
            sfn.not_(sfn.Var("$.body").string_equals("failed!"))
            # define next action
            .next_then(succeed)
        ),
        # choice 2, fail case
        (
            # define condition
            sfn.Var("$.body").string_equals("failed!")
            # define next action
            .next_then(fail)
        ),
    ])
)

# ------------------------------------------------------------------------------
# Step 4. Declare an instance of AWS State Machine for AWS console
# ------------------------------------------------------------------------------
# This is the metadata of the concrete AWS State Machine resource
state_machine = sfn.StateMachine(
    name="stepfunction_quick_start",
    workflow=workflow,
    role_arn="arn:aws:iam::669508176277:role/state-machine-role",
)

# ------------------------------------------------------------------------------
# Step 5. Deploy / Execute / Delete State Machine
# ------------------------------------------------------------------------------
# please only uncomment one line at a time

# deploy (create / update)
state_machine.deploy(bsm)

# execute state machine with custom payload
# step_function.execute(bsm, payload={"name": "alice"})

# delete state machine
# step_function.delete(bsm)
