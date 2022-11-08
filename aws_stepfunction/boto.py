# -*- coding: utf-8 -*-

"""
boto3 helpers
"""

import attr
from boto_session_manager import BotoSesManager as BSM, AwsServiceEnum


class StateMachineNotExist(Exception):
    pass


class BucketNotExist(Exception):
    pass


class IamRoleNotExist(Exception):
    pass


class CloudFormationStackNotExist(Exception):
    pass


class LambdaFunctionNotExist(Exception):
    pass


@attr.s
class BotoMan:
    bsm: BSM = attr.ib()

    @property
    def sfn_client(self):
        return self.bsm.get_client(AwsServiceEnum.SFN)

    @property
    def s3_client(self):
        return self.bsm.get_client(AwsServiceEnum.S3)

    @property
    def iam_client(self):
        return self.bsm.get_client(AwsServiceEnum.IAM)

    @property
    def cf_client(self):
        return self.bsm.get_client(AwsServiceEnum.CloudFormation)

    @property
    def lbd_client(self):
        return self.bsm.get_client(AwsServiceEnum.Lambda)

    # ------------------------------------------------------------------------------
    # S3
    # ------------------------------------------------------------------------------
    def is_s3_bucket_exists(self, name: str) -> bool:
        try:
            self.s3_client.head_bucket(Bucket=name)
            return True
        except Exception as e:
            if "Not Found" in str(e):
                return False
            else:
                raise e

    def get_s3_bucket_tags(self, name: str) -> dict:
        try:
            response = self.s3_client.get_bucket_tagging(Bucket=name)
            return {
                dct["Key"]: dct["Value"]
                for dct in response.get("TagSet", [])
            }
        except Exception as e:
            if "The specified bucket does not exist" in str(e):
                raise BucketNotExist
            else:
                raise e

    # ------------------------------------------------------------------------------
    # IAM Role
    # ------------------------------------------------------------------------------
    _iam_role_not_exists_message_pattern = "cannot be found"

    def is_iam_role_exists(self, name: str) -> bool:
        try:
            self.iam_client.get_role(RoleName=name)
            return True
        except Exception as e:
            if self._iam_role_not_exists_message_pattern in str(e):
                return False
            else:
                raise e

    def get_iam_role_tags(self, name: str) -> dict:
        try:
            response = self.iam_client.get_role(RoleName=name)
            return {
                dct["Key"]: dct["Value"]
                for dct in response.get("Tags", [])
            }
        except Exception as e:
            if self._iam_role_not_exists_message_pattern in str(e):
                raise IamRoleNotExist
            else:
                raise e

    # ------------------------------------------------------------------------------
    # Lambda Function
    # ------------------------------------------------------------------------------
    _lbd_func_not_exists_message_pattern = "Function not found"

    def is_lbd_func_exists(self, name: str) -> bool:
        try:
            self.lbd_client.get_function(FunctionName=name)
            return True
        except Exception as e:
            if self._lbd_func_not_exists_message_pattern in str(e):
                return False
            else:
                raise e

    def get_lbd_func_tags(self, name: str) -> dict:
        try:
            response = self.lbd_client.get_function(FunctionName=name)
            return response.get("Tags", {})
        except Exception as e:
            if self._lbd_func_not_exists_message_pattern in str(e):
                raise LambdaFunctionNotExist
            else:
                raise e

    # ------------------------------------------------------------------------------
    # CloudFormation Stack
    # ------------------------------------------------------------------------------
    _cloudformation_stack_not_exists_message_pattern = "does not exist"

    def is_cloudformation_stack_exists(self, name: str) -> bool:
        try:
            self.cf_client.describe_stacks(StackName=name)
            return True
        except Exception as e:
            if self._cloudformation_stack_not_exists_message_pattern in str(e):
                return False
            else:
                raise e

    def get_cloudformation_stack_tags(self, name: str) -> dict:
        try:
            response = self.cf_client.describe_stacks(StackName=name)
            return {
                dct["Key"]: dct["Value"]
                for dct in response["Stacks"][0].get("Tags", [])
            }
        except Exception as e:
            if self._cloudformation_stack_not_exists_message_pattern in str(e):
                raise CloudFormationStackNotExist
            else:
                raise e
