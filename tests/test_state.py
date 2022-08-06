# -*- coding: utf-8 -*-

import os
import pytest
from aws_stepfunction.state import (
    State, Task, Parallel, Map, Pass, Wait, Choice, Succeed, Fail
)


class TestState:
    @pytest.mark.parametrize(
        "klass",
        [
            Task, Parallel, Map, Pass, Wait, Choice, Succeed, Fail,
        ],
    )
    def test_invalid_state_id(self, klass: State):
        with pytest.raises(Exception):
            klass(id=1)


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
