# -*- coding: utf-8 -*-

import attr
from pathlib_mate import Path
from cottonformation.res import awslambda

from ..state import Task, Retry


@attr.s
class MagicTask(Task):
    pass


@attr.s
class IOHandlerTask(MagicTask):
    lbd_func_name: str = attr.ib(default=None)
    lbd_script: str = attr.ib(default=None)
    lbd_aws_account_id = attr.ib(default=None)
    lbd_aws_region = attr.ib(default=None)

    lbd_role: str = attr.ib(default=None)
    lbd_code_s3_bucket: str = attr.ib(default=None)
    lbd_code_s3_key: str = attr.ib(default=None)
    lbd_timeout: int = attr.ib(default=3)
    lbd_memory: int = attr.ib(default=128)
    lbd_runtime: str = attr.ib(default="python3.8")

    def _is_magic(self) -> bool:
        return True

    def __attrs_post_init__(self):
        self.resource = "arn:aws:states:::lambda:invoke"
        self.output_path = "$.Payload"
        self.parameters = {
            "Payload": {
                "input.$": "$",
                "context.$": "$$",
            },
            "FunctionName": (
                f"arn:aws:lambda:{self.lbd_aws_region}:{self.lbd_aws_account_id}"
                f":function:{self.lbd_func_name}"
            ),
        }
        self.retry.extend([
            (
                Retry.new()
                .with_interval_seconds(2)
                .with_back_off_rate(2)
                .with_max_attempts(3)
                .if_lambda_service_error()
                .if_lambda_aws_error()
                .if_lambda_sdk_client_error()
            )
        ])

    @property
    def path_lbd_script(self) -> Path:
        return Path(self.lbd_script).absolute()

    @property
    def lambda_handler(self) -> str:
        return f"{Path(self.lbd_script).fname}.lambda_handler"

    def lambda_function(self) -> awslambda.Function:
        return awslambda.Function(
            self.lbd_func_name.replace("_", "").replace("-", ""),
            p_FunctionName=self.lbd_func_name,
            p_Runtime=self.lbd_runtime,
            p_MemorySize=self.lbd_memory,
            p_Timeout=self.lbd_timeout,
            p_Handler=self.lambda_handler,
            rp_Role=self.lbd_role,
            rp_Code=awslambda.PropFunctionCode(
                p_S3Bucket=self.lbd_code_s3_bucket,
                p_S3Key=self.lbd_code_s3_key,
            ),
        )
