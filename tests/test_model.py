# -*- coding: utf-8 -*-

import os
import pytest

import typing as T
import attr
from aws_stepfunction.model import StepFunctionObject


@attr.s
class ToDictTestObject(StepFunctionObject):
    a_int: T.Optional[int] = attr.ib(default=None)
    a_str: T.Optional[str] = attr.ib(default=None)
    a_list: list = attr.ib(factory=list)
    a_dict: dict = attr.ib(factory=dict)


@attr.s
class KeyOrderTestObject(StepFunctionObject):
    c: int = attr.ib()
    a: int = attr.ib()
    d: int = attr.ib()
    b: int = attr.ib()

    _se_order = [
        "a",
        "b",
        "c",
        "d",
    ]


class TestStepFunctionObject:
    def test_to_dict(self):
        obj = ToDictTestObject()
        assert len(obj.to_dict()) == 0

    def test_re_order(self):
        obj = KeyOrderTestObject(a=1, b=2, c=3, d=4)
        assert (
            list(KeyOrderTestObject._re_order(obj.to_dict()))
            == KeyOrderTestObject._se_order
        )


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
