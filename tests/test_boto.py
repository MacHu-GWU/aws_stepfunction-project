# -*- coding: utf-8 -*-

import os

import pytest
from boto_session_manager import BotoSesManager
from aws_stepfunction.tests import run_cov_test
from aws_stepfunction.boto import (
    BotoMan,
    StateMachineNotExist,
    BucketNotExist,
    IamRoleNotExist,
    CloudFormationStackNotExist,
    LambdaFunctionNotExist,
)


class TestBotoMan:
    @property
    def boto_man(self) -> BotoMan:
        return BotoMan(bsm=BotoSesManager(profile_name="aws_data_lab_sanhe_us_east_1"))

    def run_test(self):
        assert self.boto_man.is_s3_bucket_exists("not-exists") is False
        assert self.boto_man.is_iam_role_exists("not-exists") is False
        assert self.boto_man.is_lbd_func_exists("not-exists") is False
        assert self.boto_man.is_cloudformation_stack_exists("not-exists") is False

    def test(self):
        if "CI" not in os.environ:
            self.run_test()


if __name__ == "__main__":
    run_cov_test(
        script=__file__,
        module="aws_stepfunction.boto"
    )
