# -*- coding: utf-8 -*-

import os
import pytest
from aws_stepfunction import constant


def test_contains():
    assert constant.TopLevelFieldEnum.contains("StartAt") is True
    assert constant.TopLevelFieldEnum.contains("InvalidField") is False


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
