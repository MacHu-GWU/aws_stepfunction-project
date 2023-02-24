# -*- coding: utf-8 -*-

from aws_console_url import AWSConsole
from boto_session_manager import BotoSesManager

bsm = BotoSesManager(profile_name="aws_data_lab_sanhe_us_east_1")


aws_console = AWSConsole(
    aws_account_id=bsm.aws_account_id,
    aws_region=bsm.aws_region,
    is_us_gov_cloud=False,
    bsm=bsm,
)
