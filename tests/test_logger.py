# -*- coding: utf-8 -*-

from aws_stepfunction.logger import logger
from aws_stepfunction.tests import run_cov_test


class MyClass:
    @logger.decorator
    def hello(self, name: str):
        logger.info(f"hello {name}")


class TestStreamLogger:
    def test(self):
        with logger.temp_disable():
            logger.debug("debug")
            logger.info("info")
            logger.warning("warning")
            logger.error("error")
            logger.critical("critical")

    def test_decorator(self):
        my_class = MyClass()
        my_class.hello(name="alice")
        my_class.hello(name="bob", verbose=False)


if __name__ == "__main__":
    run_cov_test(
        script=__file__,
        module="aws_stepfunction.logger",
    )
