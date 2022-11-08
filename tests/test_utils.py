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


def test_tokenize():
    assert utils.tokenize(" h e_l-l o    world") == ["h", "e", "l", "l", "o", "world"]


def test_slugify():
    assert utils.slugify("  Hello_World  ") == "hello-world"


def test_snake_case():
    assert utils.snake_case("  Hello-World  ") == "hello_world"


def test_camel_case():
    assert utils.camel_case("  hello_world  ") == "HelloWorld"


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
