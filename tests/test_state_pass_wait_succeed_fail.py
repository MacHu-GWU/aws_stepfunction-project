# -*- coding: utf-8 -*-

import os
import pytest

from rich import print
from aws_stepfunction import exc
from aws_stepfunction.state import Pass, Wait, Succeed, Fail


class TestPass:
    def test(self):
        task = Pass(result={"key": "value"}, next="last")
        _ = task.serialize()


class TestWait:
    def test(self):
        task = Wait(next="last")
        with pytest.raises(exc.StateValidationError):
            task.serialize()
        task.seconds = 1
        _ = task.serialize()


class TestSuceed:
    def test(self):
        task = Succeed()
        _ = task.serialize()  # suceeed state doesn't need "END"


class TestFail:
    def test(self):
        task = Fail(cause="some reason", error="unknown error")
        _ = task.serialize()  # fail state doesn't need "END"


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
        "--cov=aws_stepfunction.state",
        "--cov-report", "term-missing",
        "--cov-report", f"html:{dir_htmlcov}",
        abspath,
    ]
    subprocess.run(args)
