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

from .state import Task, Parallel
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

try:
    from s3pathlib import S3Path, context
    import cottonformation as cf
    from cottonformation.res import s3, iam

    from .magic.task import BaseLambdaTask
except ImportError:
    pass

if T.TYPE_CHECKING:  # pragma: no cover
    from .workflow import Workflow


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

    def is_express(self) -> bool:
        return self.type == "EXPRESS"

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

    @logger.decorator
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

        if self.is_express():
            execution_id = ":".join(execution_arn.split(":")[-2:])
            start_date_ts = int(res["startDate"].timestamp() * 1000)
            execution_console_url = (
                f"https://{bsm.aws_region}.console.aws.amazon.com/states/"
                f"home?region={bsm.aws_region}#/express-executions/details/"
                f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
                f"express:{self.name}:{execution_id}?startDate={start_date_ts}"
            )
        else:
            execution_id = execution_arn.split(":")[-1]
            execution_console_url = (
                f"https://{bsm.aws_region}.console.aws.amazon.com/states/"
                f"home?region={bsm.aws_region}#/v2/executions/details/"
                f"arn:aws:states:{bsm.aws_region}:{bsm.aws_account_id}:"
                f"execution:{self.name}:{execution_id}"
            )

        logger.info(f"  preview at: {execution_console_url}")
        return res

    @logger.decorator
    def deploy(self, bsm: 'BotoSesManager') -> dict:
        self._deploy_magic(bsm)
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

    @logger.decorator
    def _deploy_magic(self, bsm: 'BotoSesManager'):
        """
        Deploy magic tasks (if available)
        """
        boto_man = BotoMan(bsm=bsm)

        # detect whether the magic task is used
        logger.info("detect whether the magic task is used ...")

        def iterate_task_state(workflow: 'Workflow') -> T.Iterable[Task]:
            for _, state in workflow._states.items():
                if isinstance(state, Task):
                    yield state
                elif isinstance(state, Parallel):
                    for sub_workflow in state.branches:
                        for state_ in iterate_task_state(sub_workflow):
                            yield state_
                else:
                    pass

        lbd_task_list: T.List[BaseLambdaTask] = list()
        for state in iterate_task_state(self.workflow):
            if state._is_magic():
                if isinstance(state, BaseLambdaTask):
                    lbd_task_list.append(state)

        has_magic_task: bool = len(lbd_task_list) > 0
        if has_magic_task:
            logger.info("yes", 1)
        else:
            logger.info("no", 1)

        # First create the necessary S3 bucket,
        tpl = cf.Template()

        need_to_deploy_s3_and_iam = False

        DEFAULT_CREATE_BY = "aws-stepfunction-python-sdk"

        if has_magic_task:
            logger.info("identify necessary S3 bucket and IAM role ...")

            # create necessary S3 Bucket
            s3_bucket_set: T.Set[str] = set()
            for state in lbd_task_list:
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
                    logger.info(f"need to create S3 Bucket {bucket_name!r}", 1)

                if need_to_declare_this_bucket:
                    s3_bucket = s3.Bucket(
                        f"S3Bucket{camel_case(bucket_name)}",
                        p_BucketName=bucket_name,
                    )
                    # logger.info(f"declare S3 Bucket {s3_bucket.p_BucketName}")
                    tpl.add(s3_bucket)

            # create necessary IAM role
            need_default_iam_role = False
            for state in lbd_task_list:
                if state.lbd_role is None:
                    need_default_iam_role = True
                    logger.info("we need a default IAM role for lambda function", 1)
                    break

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
                    logger.info(f"need to create IAM Role {boto_man.default_iam_role_magic_task!r}", 1)

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
                    # print(f"declare IAM Role {default_role.p_RoleName}")
                    tpl.add(default_role)
            logger.info("done", 1)

        if need_to_deploy_s3_and_iam:
            self._deploy_cft(
                bsm=bsm,
                tpl=tpl,
                msg="deploy S3 and IAM ...",
                period=5,
                retry=12,
            )

        logger.info("deploy Lambda Functions ...")
        context.attach_boto_session(bsm.boto_ses)
        dir_home = Path.home()
        dir_home_tmp = dir_home / "tmp"
        logger.info("upload lambda deployment artifacts ...", 1)
        for state in lbd_task_list:
            path = dir_home_tmp.joinpath(f"{state.path_lbd_script.md5}.zip")
            state.path_lbd_script.make_zip_archive(
                dst=path.abspath,
                makedirs=True,
                include_dir=True,
                overwrite=True,
                compress=True,
                verbose=False,
            )
            # Don't update the state object directly!
            if state.lbd_role is None:
                lbd_role = boto_man.default_iam_role_arn_magic_task
            else:
                lbd_role = state.lbd_role
            if state.lbd_code_s3_bucket is None:
                lbd_code_s3_bucket = boto_man.default_s3_bucket_artifacts
                lbd_code_s3_key = f"{boto_man.default_s3_bucket_artifacts_prefix}/{path.md5}.zip"
            else:
                lbd_code_s3_bucket = state.lbd_code_s3_bucket
                lbd_code_s3_key = state.lbd_code_s3_key
            s3path = S3Path(lbd_code_s3_bucket, lbd_code_s3_key)
            logger.info(f"upload from {path} to {s3path.uri}", 2)
            s3path.upload_file(path.abspath, overwrite=True)

            new_state = attr.evolve(
                state,
                lbd_role=lbd_role,
                lbd_code_s3_bucket=lbd_code_s3_bucket,
                lbd_code_s3_key=lbd_code_s3_key,
            )
            lbd_func = new_state.lambda_function()
            lbd_func.update_tags(
                overwrite_existing=True,
                hash=state.path_lbd_script.md5,
            )
            logger.info(f"declare Lambda Function {lbd_func.p_FunctionName}", 2)
            tpl.add(lbd_func)

        self._deploy_cft(
            bsm=bsm,
            tpl=tpl,
            msg="deploy magic task Lambda Function ...",
            period=5,
            retry=12,
        )

    def _deploy_cft(
        self,
        bsm: BotoSesManager,
        tpl: 'cf.Template',
        msg: str,
        period: int,
        retry: int,
    ):
        """
        A syntax sugar that deploy ``cottonformation.Template``.
        """
        logger.info(msg)
        tpl.batch_tagging(
            overwrite_existing=True,
            CreatedBy="aws-stepfunction-python-sdk",
        )
        env = cf.Env(bsm=bsm)
        boto_man = BotoMan(bsm=bsm)
        try:
            stack_console_url = (
                f"https://console.aws.amazon.com/cloudformation/home?"
                f"region={bsm.aws_region}#/stacks?"
                f"filteringStatus=active&"
                f"filteringText={self._stack_name}&"
                f"viewNested=true&"
                f"hideStacks=false&"
                f"stackId="
            )
            logger.info(f"preview cloudformation stack status: {stack_console_url}", 1)
            env.deploy(
                template=tpl,
                stack_name=self._stack_name,
                include_iam=True,
                verbose=False,
            )
            boto_man.wait_cloudformation_stack_success(
                name=self._stack_name,
                period=period,
                retry=retry,
            )
            logger.info("done", 1)
        except Exception as e:
            if "No updates are to be performed" in str(e):
                logger.info("no updates are to be performed", 1)
            else:
                raise e
