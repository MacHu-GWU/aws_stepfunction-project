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
    a_empty_str: T.Optional[str] = attr.ib(default="")
    a_list: list = attr.ib(factory=list)
    a_dict: dict = attr.ib(factory=dict)
    _cache: dict = attr.ib(factory=dict)


@attr.s
class ToAliasTestObject(StepFunctionObject):
    a: int = attr.ib()
    b: int = attr.ib(metadata={"alias": "bob"})


@attr.s
class KeyOrderTestObject(StepFunctionObject):
    c: int = attr.ib()
    a: int = attr.ib()
    d: int = attr.ib()
    b: int = attr.ib()

    _field_order = [
        "a",
        "b",
        "c",
        "d",
    ]


class TestStepFunctionObject:
    def test_to_dict(self):
        obj = ToDictTestObject()
        assert len(obj.to_dict()) == 0

    def test_to_alias(self):
        obj = ToAliasTestObject(a=1, b=2)
        data = ToAliasTestObject._to_alias(obj.to_dict())
        assert data == {"a": 1, "bob": 2}

    def test_re_order(self):
        obj = KeyOrderTestObject(a=1, b=2, c=3, d=4)
        assert (
            list(KeyOrderTestObject._sort_field(obj.to_dict()))
            == KeyOrderTestObject._field_order
        )

        obj = ToDictTestObject(
            a_int=1,
            a_str="abc",
            a_empty_str="xyz",
            a_list=[1, 2, 3],
            a_dict={"a": 1},
            cache={"key": "value"},
        )
        assert (
            list(ToDictTestObject._sort_field(obj.to_dict()))
            == [
                "a_int",
                "a_str",
                "a_empty_str",
                "a_list",
                "a_dict",
            ]
        )


if __name__ == "__main__":
    import sys
    import subprocess

    abspath = os.path.abspath(__file__)
    dir_project_root = os.path.dirname(abspath)
    for _ in range(10):
        if os.path.exists(os.path.join(dir_project_root, ".git")):
            break
        else:
            dir_project_root = os.path.dirname(dir_project_root)
    else:
        raise FileNotFoundError("cannot find project root dir!")
    dir_htmlcov = os.path.join(dir_project_root, "htmlcov")
    bin_pytest = os.path.join(os.path.dirname(sys.executable), "pytest")

    args = [
        bin_pytest,
        "-s", "--tb=native",
        f"--rootdir={dir_project_root}",
        "--cov=aws_stepfunction.model",
        "--cov-report", "term-missing",
        "--cov-report", f"html:{dir_htmlcov}",
        abspath,
    ]
    subprocess.run(args, check=True)
