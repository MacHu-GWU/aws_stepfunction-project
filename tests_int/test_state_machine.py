# -*- coding: utf-8 -*-

"""
Last tested on 2022-08-06, 100% coverage

.. note::

    it takes around 30 seconds to completely delete a state machine.
    wait 30 seconds between each integration test.
"""

import os
import time
import aws_stepfunction as sfn
from boto_session_manager import BotoSesManager


def test():
    bsm = BotoSesManager(
        profile_name="aws_data_lab_sanhe_us_east_1",
        region_name="us-east-1",
    )

    sfn.task_context.aws_account_id = bsm.aws_account_id
    sfn.task_context.aws_region = bsm.aws_region

    workflow = sfn.Workflow(comment="aws_stepfunction integrate test 1")

    succeed = sfn.Succeed()
    fail = sfn.Fail()

    (
        workflow.start_from(sfn.Pass())
        .parallel([
            workflow.subflow_from(sfn.Pass()).next_then(sfn.Pass()).end(),
            workflow.subflow_from(sfn.Pass()).next_then(sfn.Pass()).end(),
        ])
        .next_then(sfn.Pass(result={"items": [1, 2, 3]}))
        .map(
            workflow.subflow_from(sfn.Pass()).next_then(sfn.Pass()).end(),
            items_path="$.items",
        )
        .next_then(sfn.Pass())
        .choice([
            (
                sfn.Var("$.flag").is_present()
                .next_then(succeed)
            ),
            (
                sfn.not_(sfn.Var("$.flag").is_present())
                .next_then(fail)
            ),
        ])
    )

    state_machine = sfn.StateMachine(
        name="stepfunction-int-test",
        workflow=workflow,
        role_arn="arn:aws:iam::669508176277:role/sanhe-for-everything-admin",
        tags=dict(Creator="alice@example.com")
    )

    state_machine.deploy(bsm)
    time.sleep(3)

    workflow.comment = "aws_stepfunction integrate test 2"
    state_machine.deploy(bsm)
    time.sleep(3)

    state_machine.execute(bsm, payload={"name": "alice"})
    time.sleep(3)

    state_machine.delete(bsm)
    time.sleep(3)


if __name__ == "__main__":
    import sys
    import subprocess

    abspath = os.path.abspath(__file__)
    dir_project_root = os.path.dirname(abspath)
    for _ in range(10):
        if os.path.exists(os.path.join(dir_project_root, ".git")):
            break
        else:
            dir_project_root = os.path.dirname(dir_project_root)
    else:
        raise FileNotFoundError("cannot find project root dir!")
    dir_htmlcov = os.path.join(dir_project_root, "htmlcov")
    bin_pytest = os.path.join(os.path.dirname(sys.executable), "pytest")

    args = [
        bin_pytest,
        "-s", "--tb=native",
        f"--rootdir={dir_project_root}",
        "--cov=aws_stepfunction.state_machine",
        "--cov-report", "term-missing",
        "--cov-report", f"html:{dir_htmlcov}",
        abspath,
    ]
    subprocess.run(args)
