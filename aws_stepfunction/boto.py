# -*- coding: utf-8 -*-

"""
boto3 helpers.
"""

import time
import attr
from boto_session_manager import BotoSesManager as BSM, AwsServiceEnum

from .logger import logger


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
    """
    Simple wrapper around boto3 API.
    """
    bsm: BSM = attr.ib()

    @property
    def default_s3_bucket_artifacts(self) -> str:
        """
        The default s3 bucket that stores the temporary artifacts.
        """
        return f"{self.bsm.aws_account_id}-{self.bsm.aws_region}-aws-stepfunction-python-sdk"

    @property
    def default_s3_bucket_artifacts_prefix(self) -> str:
        return "aws-stepfunction-python-sdk"

    @property
    def default_iam_role_magic_task(self) -> str:
        """
        The default iam role for magic task lambda function.
        """
        return "aws-stepfunction-python-sdk-magic-task-role"

    @property
    def default_iam_role_arn_magic_task(self) -> str:
        """
        The default iam role arn for magic task lambda function.
        """
        return f"arn:aws:iam::{self.bsm.aws_account_id}:role/{self.default_iam_role_magic_task}"

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
                for dct in response["Role"].get("Tags", [])
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

    def get_cloudformation_stack_status(self, name: str) -> str:
        """
        Get CloudFormation stack status.

        possible status: 'CREATE_IN_PROGRESS'|'CREATE_FAILED'|'CREATE_COMPLETE'|'ROLLBACK_IN_PROGRESS'|'ROLLBACK_FAILED'|'ROLLBACK_COMPLETE'|'DELETE_IN_PROGRESS'|'DELETE_FAILED'|'DELETE_COMPLETE'|'UPDATE_IN_PROGRESS'|'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS'|'UPDATE_COMPLETE'|'UPDATE_FAILED'|'UPDATE_ROLLBACK_IN_PROGRESS'|'UPDATE_ROLLBACK_FAILED'|'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS'|'UPDATE_ROLLBACK_COMPLETE'|'REVIEW_IN_PROGRESS'|'IMPORT_IN_PROGRESS'|'IMPORT_COMPLETE'|'IMPORT_ROLLBACK_IN_PROGRESS'|'IMPORT_ROLLBACK_FAILED'|'IMPORT_ROLLBACK_COMPLETE'

        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#stack
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
        """
        try:
            response = self.cf_client.describe_stacks(StackName=name)
            return response["Stacks"][0]["StackStatus"]
        except Exception as e:
            if self._cloudformation_stack_not_exists_message_pattern in str(e):
                raise CloudFormationStackNotExist
            else:
                raise e

    @logger.decorator
    def wait_cloudformation_stack_success(
        self,
        name: str,
        period: int = 5,
        retry: int = 2,
        _indent: int = 0,
    ):
        """
        Wait a cloudformation stack to reach "success" status.
        """
        logger.info(f"wait {name!r} stack to complete ... ", _indent)
        for ith in range(retry):
            logger.info(f"elapsed {ith * period} seconds ...", _indent + 1)
            time.sleep(period)
            stack_status = self.get_cloudformation_stack_status(name)
            if stack_status in [
                "CREATE_COMPLETE",
                "UPDATE_COMPLETE",
                "DELETE_COMPLETE",
            ]:
                return
        raise TimeoutError(
            f"the cloudformation stack never reach success state, "
            f"timed out after {period * retry} seconds"
        )
