# -*- coding: utf-8 -*-

from aws_stepfunction.logger import logger
from aws_stepfunction.tests import run_cov_test


class TestStreamLogger:
    def test(self):
        with logger.temp_disable():
            logger.debug("debug")
            logger.info("info")
            logger.warning("warning")
            logger.error("error")
            logger.critical("critical")


if __name__ == "__main__":
    run_cov_test(
        script=__file__,
        module="aws_stepfunction.logger",
    )
