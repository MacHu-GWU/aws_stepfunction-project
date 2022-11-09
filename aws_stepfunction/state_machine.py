# -*- coding: utf-8 -*-

"""
State Machine management module
"""

import typing as T
import json
import time

import attr
import attr.validators as vs
from pathlib_mate import Path
from boto_session_manager import BotoSesManager, AwsServiceEnum

from .model import StepFunctionObject
from .constant import Constant as C
from .logger import logger
from .utils import slugify, snake_case, camel_case
from .boto import (
    BotoMan,
    StateMachineNotExist,
    BucketNotExist,
    IamRoleNotExist,
    CloudFormationStackNotExist,
    LambdaFunctionNotExist,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from .workflow import Workflow

from s3pathlib import S3Path, context
import cottonformation as cf
from cottonformation.res import s3, iam

from .magic.task import MagicTask, IOHandlerTask


@attr.s
class StateMachine(StepFunctionObject):
    """
    Represent an instance of State Machine in AWS Console.

    :param name:
    :param workflow: :class:`~aws_stepfunction.workflow.Workflow`
    :param role_arn:
    :param type:
    :param logging_configuration:
    :param tracing_configuration:
    :param tags:
    """
    name: str = attr.ib()
    workflow: 'Workflow' = attr.ib()
    role_arn: str = attr.ib(
        metadata={C.ALIAS: "roleArn"},
    )
    type: T.Optional[str] = attr.ib(default="STANDARD")
    logging_configuration: T.Optional[dict] = attr.ib(
        default=None, metadata={C.ALIAS: "loggingConfiguration"},
    )
    tracing_configuration: T.Optional[dict] = attr.ib(
        default=None, metadata={C.ALIAS: "tracingConfiguration"},
    )
    tags: T.Optional[dict] = attr.ib(
        default=None,
        validator=vs.optional(vs.deep_mapping(
            key_validator=vs.instance_of(str),
            value_validator=vs.instance_of(str),
        ))
    )

    def set_type_as_standard(self) -> 'StateMachine':  # pragma: no cover
        self.type = "STANDARD"
        return self

    def set_type_as_express(self) -> 'StateMachine':  # pragma: no cover
        self.type = "EXPRESS"
        return self

    def _convert_tags(self) -> T.List[T.Dict[str, str]]:
        return [
            dict(key=key, value=value)
            for key, value in self.tags.items()
        ]

    def get_state_machine_arn(self, bsm: 'BotoSesManager') -> str:
        return (
            f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
            f"stateMachine:{self.name}"
        )

    def get_state_machine_console_url(self, bsm: 'BotoSesManager') -> str:
        return (
            f"https://{bsm.aws_region}.console.aws.amazon.com/states/"
            f"home?region={bsm.aws_region}#/statemachines/view/"
            f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
            f"stateMachine:{self.name}"
        )

    def get_state_machine_visual_editor_console_url(self, bsm: 'BotoSesManager') -> str:
        return (
            f"https://{bsm.aws_region}.console.aws.amazon.com/states/"
            f"home?region={bsm.aws_region}#/visual-editor?stateMachineArn="
            f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
            f"stateMachine:{self.name}"
        )

    def describe(self, bsm: 'BotoSesManager'):
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        return sfn_client.describe_state_machine(
            stateMachineArn=self.get_state_machine_arn(bsm)
        )

    def exists(self, bsm: 'BotoSesManager') -> bool:
        """
        Check if the state machine exists.
        """
        try:
            self.describe(bsm)
            return True
        except Exception as e:
            if "StateMachineDoesNotExist" in e.__class__.__name__:
                return False
            else:  # pragma: no cover
                raise e

    def create(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.create_state_machine
        """
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        kwargs = self.to_dict()
        kwargs = self._to_alias(kwargs)
        kwargs.pop("workflow")
        kwargs["definition"] = json.dumps(self.workflow.serialize())
        if self.tags:
            kwargs["tags"] = self._convert_tags()
        return sfn_client.create_state_machine(**kwargs)

    def update(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.update_state_machine
        """
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        kwargs = self.to_dict()
        kwargs = self._to_alias(kwargs)
        kwargs["stateMachineArn"] = f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:stateMachine:{self.name}"
        kwargs.pop("name")
        kwargs.pop("type")
        kwargs.pop("workflow")
        kwargs["definition"] = json.dumps(self.workflow.serialize())
        if self.tags:
            kwargs.pop("tags")
        return sfn_client.update_state_machine(**kwargs)

    def delete(self, bsm: 'BotoSesManager'):
        """
        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.delete_state_machine
        """
        state_machine_arn = self.get_state_machine_arn(bsm)
        logger.info(f"delete state machine {state_machine_arn!r}")
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        res = sfn_client.delete_state_machine(stateMachineArn=state_machine_arn)
        logger.info(f"  done, exam at: {self.get_state_machine_console_url(bsm)}")
        return res

    def execute(
        self,
        bsm: 'BotoSesManager',
        payload: T.Optional[dict] = None,
        name: T.Optional[str] = None,
        sync: bool = False,
        trace_header: T.Optional[str] = None,
    ):
        """
        Execute state machine with custom payload.

        :param payload: custom payload in python dictionary
        :param name: the execution name, recommend to leave it empty and
            let step function to generate an uuid for you.
        :param sync: if true, you need to wait for the execution to finish
            otherwise, it returns immediately, and you can check the status
            in the console

        Reference:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.start_execution
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html#SFN.Client.start_sync_execution
        """
        state_machine_arn = self.get_state_machine_arn(bsm)
        logger.info(f"execute state machine {state_machine_arn!r}")
        sfn_client = bsm.get_client(AwsServiceEnum.SFN)
        kwargs = dict(stateMachineArn=state_machine_arn)
        if payload is not None:
            kwargs["input"] = json.dumps(payload)
        if name is not None:  # pragma: no cover
            kwargs["name"] = name
        if trace_header is not None:  # pragma: no cover
            kwargs["traceHeader"] = trace_header

        if sync:  # pragma: no cover
            res = sfn_client.start_sync_execution(**kwargs)
        else:
            res = sfn_client.start_execution(**kwargs)
        execution_arn = res["executionArn"]
        execution_id = execution_arn.split(":")[-1]
        execution_console_url = (
            f"https://{bsm.aws_region}.console.aws.amazon.com/states/"
            f"home?region={bsm.aws_region}#/executions/details/"
            f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
            f"execution:{self.name}:{execution_id}"
        )
        logger.info(f"  preview at: {execution_console_url}")
        return res

    def deploy(self, bsm: 'BotoSesManager') -> dict:
        logger.info(
            f"deploy state machine to {self.get_state_machine_arn(bsm)!r} ..."
        )
        if self.exists(bsm):
            logger.info("  already exists, update state machine ...")
            res = self.update(bsm)
            logger.info(f"  done, preview at: {self.get_state_machine_visual_editor_console_url(bsm)}")
            res["_deploy_action"] = "update"
        else:
            logger.info("  not exists, create state machine ...")
            res = self.create(bsm)
            res["_deploy_action"] = "create"
            logger.info(f"  done, preview at: {self.get_state_machine_visual_editor_console_url(bsm)}")
        return res

    # -------------------------------------------------------------------------
    # Magic Task
    # -------------------------------------------------------------------------
    @property
    def _stack_name(self) -> str:
        """
        Magic task cloudFormation stack name.
        """
        return slugify(self.name)

    def _get_stack_status(self, bsm: 'BotoSesManager') -> str:
        """
        Ref:

        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#stack
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
        """
        cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
        stack = bsm.boto_ses.resource("cloudformation").Stack(self._stack_name)
        # "'CREATE_IN_PROGRESS'|'CREATE_FAILED'|'CREATE_COMPLETE'|'ROLLBACK_IN_PROGRESS'|'ROLLBACK_FAILED'|'ROLLBACK_COMPLETE'|'DELETE_IN_PROGRESS'|'DELETE_FAILED'|'DELETE_COMPLETE'|'UPDATE_IN_PROGRESS'|'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS'|'UPDATE_COMPLETE'|'UPDATE_FAILED'|'UPDATE_ROLLBACK_IN_PROGRESS'|'UPDATE_ROLLBACK_FAILED'|'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS'|'UPDATE_ROLLBACK_COMPLETE'|'REVIEW_IN_PROGRESS'|'IMPORT_IN_PROGRESS'|'IMPORT_COMPLETE'|'IMPORT_ROLLBACK_IN_PROGRESS'|'IMPORT_ROLLBACK_FAILED'|'IMPORT_ROLLBACK_COMPLETE',
        return stack.stack_status

    def _wait_stack_until_success(
        self,
        bsm: 'BotoSesManager',
        period: int = 1,
        retry: int = 3,
    ):
        for ith in range(retry):
            print(f"wait {self._stack_name!r} stack to complete, elapsed {ith * period} ...")
            time.sleep(period)
            stack_status = self._get_stack_status(bsm)
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

    def _deploy_magic(self, bsm: 'BotoSesManager'):
        boto_man = BotoMan(bsm=bsm)

        # detect whether the magic task is used
        io_handler_task_list: T.List[IOHandlerTask] = list()
        for state_id, state in self.workflow._states.items():
            if state._is_magic():
                if isinstance(state, IOHandlerTask):
                    io_handler_task_list.append(state)

        has_magic_task: bool = len(io_handler_task_list) > 0

        # First create the necessary S3 bucket,
        tpl = cf.Template()
        env = cf.Env(bsm=bsm)

        need_to_deploy_s3_and_iam = False

        DEFAULT_CREATE_BY = "aws-stepfunction-python-sdk"

        if has_magic_task:
            # create necessary S3 Bucket
            s3_bucket_set: T.Set[str] = set()
            for state in io_handler_task_list:
                if state.lbd_code_s3_bucket is None:
                    bucket_name = boto_man.default_s3_bucket_artifacts
                else:
                    bucket_name = state.lbd_code_s3_bucket
                s3_bucket_set.add(bucket_name)

            for bucket_name in s3_bucket_set:
                try:
                    tags = boto_man.get_s3_bucket_tags(bucket_name)
                    if tags.get("CreatedBy", "unknown") == DEFAULT_CREATE_BY:
                        need_to_declare_this_bucket = True
                    else:
                        need_to_declare_this_bucket = False
                except BucketNotExist:
                    need_to_declare_this_bucket = True
                    need_to_deploy_s3_and_iam = True

                if need_to_declare_this_bucket:
                    s3_bucket = s3.Bucket(
                        f"S3Bucket{camel_case(bucket_name)}",
                        p_BucketName=bucket_name,
                    )
                    print(f"declare S3 Bucket {s3_bucket.p_BucketName}")
                    tpl.add(s3_bucket)

            # create necessary IAM role
            need_default_iam_role = False
            for state in io_handler_task_list:
                if state.lbd_role is None:
                    need_default_iam_role = True

            if need_default_iam_role:
                try:
                    tags = boto_man.get_iam_role_tags(boto_man.default_iam_role_magic_task)
                    if tags.get("CreatedBy", "unknown") == DEFAULT_CREATE_BY:
                        need_to_declare_default_iam_role = True
                    else:
                        need_to_declare_default_iam_role = False
                except IamRoleNotExist:
                    need_to_declare_default_iam_role = True
                    need_to_deploy_s3_and_iam = True

                if need_to_declare_default_iam_role:
                    default_role = iam.Role(
                        "DefaultLambdaRole",
                        rp_AssumeRolePolicyDocument=cf.helpers.iam.AssumeRolePolicyBuilder(
                            cf.helpers.iam.ServicePrincipal.awslambda(),
                        ).build(),
                        p_RoleName=boto_man.default_iam_role_magic_task,
                        p_ManagedPolicyArns=[
                            cf.helpers.iam.AwsManagedPolicy.AWSLambdaBasicExecutionRole
                        ]
                    )
                    print(f"declare IAM Role {default_role.p_RoleName}")
                    tpl.add(default_role)

        if need_to_deploy_s3_and_iam:
            print("Deploy S3 and IAM")
            tpl.batch_tagging(
                overwrite_existing=True,
                CreatedBy="aws-stepfunction-python-sdk",
            )
            try:
                env.deploy(
                    template=tpl,
                    stack_name=self._stack_name,
                    include_iam=True,
                )
                self._wait_stack_until_success(bsm, period=5, retry=6)
            except Exception as e:
                if "No updates are to be performed" in str(e):
                    print("no updates are to be performed")
                else:
                    raise e

        context.attach_boto_session(bsm.boto_ses)
        dir_home = Path.home()
        dir_home_tmp = dir_home / "tmp"
        for state in io_handler_task_list:
            state: IOHandlerTask
            if state.lbd_role is None:
                state.lbd_role = boto_man.default_iam_role_arn_magic_task
            if state.lbd_code_s3_bucket is None:
                state.lbd_code_s3_bucket = boto_man.default_s3_bucket_artifacts
                state.lbd_code_s3_key = f"{boto_man.default_s3_bucket_artifacts_prefix}/{state.path_lbd_script.md5}.zip"
            s3path = S3Path(state.lbd_code_s3_bucket, state.lbd_code_s3_key)
            path = dir_home_tmp.joinpath(f"{state.path_lbd_script.md5}.zip")
            state.path_lbd_script.make_zip_archive(
                dst=path.abspath,
                makedirs=True,
                overwrite=True,
                compress=True,
                verbose=False,
            )
            s3path.upload_file(path.abspath, overwrite=True)

            lbd_func = state.lambda_function()
            lbd_func.update_tags(
                overwrite_existing=True,
                hash=state.path_lbd_script.md5,
            )
            print(f"declare Lambda Function {lbd_func.p_FunctionName}")
            tpl.add(lbd_func)

        tpl.batch_tagging(
            overwrite_existing=True,
            CreatedBy="aws-stepfunction-python-sdk",
        )
        print("Deploy magic task lambda function ...")
        try:
            env.deploy(
                template=tpl,
                stack_name=self._stack_name,
                include_iam=True,
            )
            self._wait_stack_until_success(bsm, period=5, retry=6)
        except Exception as e:
            if "No updates are to be performed" in str(e):
                print("no updates are to be performed")
            else:
                raise e
