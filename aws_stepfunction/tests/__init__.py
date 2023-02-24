# -*- coding: utf-8 -*-

from aws_console_url import AWSConsole

from .helper import run_cov_test
from .boto_ses import bsm

aws_console = AWSConsole(
    aws_account_id=bsm.aws_account_id,
    aws_region=bsm.aws_region,
    is_us_gov_cloud=False,
    bsm=bsm,
)
