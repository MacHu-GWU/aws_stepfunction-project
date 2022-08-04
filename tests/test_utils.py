# -*- coding: utf-8 -*-

import os
import pytest
from aws_stepfunction import utils


def test_short_uuid():
    assert len(utils.short_uuid(n=7)) == 7


def test_is_json_path():
    assert utils.is_json_path("$")
    assert utils.is_json_path("$.key")
    assert utils.is_json_path("abc") is False


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
