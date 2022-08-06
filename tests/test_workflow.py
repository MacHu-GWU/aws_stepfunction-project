# -*- coding: utf-8 -*-

import os
import pytest

from rich import print as rprint

from aws_stepfunction import exc
from aws_stepfunction.workflow import Workflow
from aws_stepfunction.state import (
    Task, Parallel, Map, Pass, Wait, Choice, Succeed, Fail,
)
from aws_stepfunction.constant import Constant as C
from aws_stepfunction.choice_rule import Var


@pytest.fixture
def wf() -> 'Workflow':
    return Workflow()


@pytest.fixture
def t1() -> 'Task':
    return Task(id="task1", resource="arn")


@pytest.fixture
def t2() -> 'Task':
    return Task(id="task2", resource="arn")


@pytest.fixture
def pass_() -> 'Pass':
    return Pass(id=C.Pass)


@pytest.fixture
def wait() -> 'Wait':
    return Wait(id="wait", seconds=1)


@pytest.fixture
def succeed() -> 'Succeed':
    return Succeed(id="succeed")


@pytest.fixture
def fail() -> 'Fail':
    return Fail(id="fail")


class TestWorkflow:
    def test_add_and_remove(self, wf, t1):
        wf._add_state(t1)
        with pytest.raises(exc.WorkflowError):
            wf._add_state(t1)
        wf._add_state(t1, ignore_exists=True)

        wf._remove_state(t1)
        with pytest.raises(exc.WorkflowError):
            wf._remove_state(t1)
        wf._remove_state(t1, ignore_not_exists=True)

    def test_cannot_go_next_if_not_started(self, wf, pass_):
        with pytest.raises(exc.WorkflowError):
            wf.next_then(pass_)

    def test_succeed_from_begin(self, wf):
        wf.succeed(id="succeed")
        _ = wf.serialize()

    def test_fail_from_begin(self, wf):
        wf.fail(id="succeed")
        _ = wf.serialize()

    def test_wait_from_begin(self, wf):
        wf.wait(seconds=1, id="wait").end()
        _ = wf.serialize()

    def test_serialize_empty_workflow(self, wf):
        with pytest.raises(exc.WorkflowValidationError):
            wf.serialize()

    def test_succeed_end(self, wf, t1, t2):
        wf.start_from(t1).wait(seconds=1).next_then(t2).succeed()
        wf.serialize()

    def test_fail_end(self, wf, t1, t2):
        wf.start_from(t1).wait(seconds=1).next_then(t2).fail()
        wf.serialize()

    def test_simple_chain(self, wf, t1, t2):
        wf.comment = "this is comment"
        wf.version = "1.0"
        wf.timeout_seconds = 60
        wf.start_from(t1).next_then(t2).end()
        wf.serialize()

    def test_pre_serialize_validation(self):
        with pytest.raises(exc.WorkflowValidationError):
            Workflow().serialize()

        with pytest.raises(exc.WorkflowValidationError):
            Workflow(start_at="nothing").serialize()

    def test_parallel_in_the_middle(self, wf):
        """
        parallel start from middle, and has next state
        """
        (
            wf.start_from(Pass(id="t1"))
            .parallel(
                [
                    (
                        wf.subflow_from(Pass(id="t21-a"))
                        .next_then(Pass(id="t21-b"))
                        .end()
                    ),
                    (
                        wf.subflow_from(Pass(id="t22-a"))
                        .next_then(Pass(id="t22-b"))
                        .end()
                    ),
                ],
                id="para",
            )
            .next_then(Pass(id="t3"))
            .end()
        )
        assert wf.serialize() == {
            C.StartAt: "t1",
            C.States: {
                "t1": {C.Type: C.Pass, C.Next: "para"},
                "para": {
                    C.Type: C.Parallel,
                    C.Branches: [
                        {
                            C.StartAt: "t21-a",
                            C.States: {
                                "t21-a": {C.Type: C.Pass, C.Next: "t21-b"},
                                "t21-b": {C.Type: C.Pass, C.End: True},
                            }
                        },
                        {
                            C.StartAt: "t22-a",
                            C.States: {
                                "t22-a": {C.Type: C.Pass, C.Next: "t22-b"},
                                "t22-b": {C.Type: C.Pass, C.End: True},
                            }
                        }
                    ],
                    C.Next: "t3",
                },
                "t3": {C.Type: C.Pass, C.End: True},
            }
        }

    def test_parallel_is_the_only_state(self, wf):
        (
            wf.start_from_parallel(
                [
                    (
                        wf.subflow_from(Pass(id="t21-a"))
                        .next_then(Pass(id="t21-b"))
                        .end()
                    ),
                    (
                        wf.subflow_from(Pass(id="t22-a"))
                        .next_then(Pass(id="t22-b"))
                        .end()
                    ),
                ],
                id="para",
            )
            .end()
        )
        assert wf.serialize() == {
            C.StartAt: "para",
            C.States: {
                "para": {
                    C.Type: C.Parallel,
                    C.Branches: [
                        {
                            C.StartAt: "t21-a",
                            C.States: {
                                "t21-a": {C.Type: C.Pass, C.Next: "t21-b"},
                                "t21-b": {C.Type: C.Pass, C.End: True},
                            }
                        },
                        {
                            C.StartAt: "t22-a",
                            C.States: {
                                "t22-a": {C.Type: C.Pass, C.Next: "t22-b"},
                                "t22-b": {C.Type: C.Pass, C.End: True},
                            }
                        }
                    ],
                    C.End: True,
                },
            }
        }

    def test_map_in_the_middle(self, wf):
        (
            wf.start_from(Pass(id="t1"))
            .map(
                (
                    wf.subflow_from(Pass(id="t21"))
                    .next_then(Pass(id="t22"))
                    .end()
                ),
                id="map",
            )
            .next_then(Pass(id="t3"))
            .end()
        )
        assert wf.serialize() == {
            C.StartAt: "t1",
            C.States: {
                "t1": {C.Type: C.Pass, C.Next: "map"},
                "map": {
                    C.Type: C.Map,
                    C.Iterator: {
                        C.StartAt: "t21",
                        C.States: {
                            "t21": {C.Type: C.Pass, C.Next: "t22"},
                            "t22": {C.Type: C.Pass, C.End: True},
                        }
                    },
                    C.Next: "t3"
                },
                "t3": {C.Type: C.Pass, C.End: True},
            }
        }

    def test_map_is_the_only_state(self, wf):
        (
            wf.start_from_map(
                (
                    wf.subflow_from(Pass(id="t1"))
                    .next_then(Pass(id="t2"))
                    .end()
                ),
                id="map",
            )
            .end()
        )
        assert wf.serialize() == {
            C.StartAt: "map",
            C.States: {
                "map": {
                    C.Type: C.Map,
                    C.Iterator: {
                        C.StartAt: "t1",
                        C.States: {
                            "t1": {C.Type: C.Pass, C.Next: "t2"},
                            "t2": {C.Type: C.Pass, C.End: True},
                        }
                    },
                    C.End: True
                },
            }
        }

    def test_choice_in_the_middle(self, wf):
        t1 = Pass(id="t1")
        t21_a = Pass(id="t21_a")
        t21_b = Pass(id="t21_b")
        t22 = Pass(id="t22")
        t3 = Pass(id="t3")
        (
            wf.start_from(t1)
            .choice(
                [
                    (
                        Var("$.key").is_present()
                        .next_then(t21_a)
                    )
                ],
                default=t22,
                id="choice",
            )
        )

        (
            wf.continue_from(t21_a)
            .next_then(t21_b)
            .next_then(t3)
        )

        (
            wf.continue_from(t22)
            .next_then(t3)
            .end()
        )

        assert wf.serialize() == {
            C.StartAt: "t1",
            C.States: {
                "t1": {C.Type: C.Pass, C.Next: "choice"},
                "choice": {
                    C.Type: C.Choice,
                    C.Choices: [
                        {C.Variable: "$.key", C.IsPresent: True, C.Next: "t21_a"}
                    ],
                    C.Default: "t22"
                },
                "t21_a": {C.Type: C.Pass, C.Next: "t21_b"},
                "t21_b": {C.Type: C.Pass, C.Next: "t3"},
                "t3": {C.Type: C.Pass, C.End: True},
                "t22": {C.Type: C.Pass, C.Next: "t3"}
            }
        }

    def test_choice_is_the_only_state(self, wf):
        t1_a = Pass(id="t1_a")
        t1_b = Pass(id="t1_b")
        t2 = Pass(id="t2")
        (
            wf.start_from_choice(
                [
                    (
                        Var("$.key").is_present()
                        .next_then(t1_a)
                    )
                ],
                default=t2,
                id="choice",
            )
        )

        (
            wf.continue_from(t1_a)
            .next_then(t1_b)
            .end()
        )

        (
            wf.continue_from(t2)
            .end()
        )

        assert wf.serialize() == {
            C.StartAt: "choice",
            C.States: {
                "choice": {
                    C.Type: C.Choice,
                    C.Choices: [
                        {C.Variable: "$.key", C.IsPresent: True, C.Next: "t1_a"}
                    ],
                    C.Default: "t2"
                },
                "t1_a": {C.Type: C.Pass, C.Next: "t1_b"},
                "t1_b": {C.Type: C.Pass, C.End: True},
                "t2": {C.Type: C.Pass, C.End: True},
            }
        }

    def test_choice_call_next_then_immediately(self, wf):
        t1_a = Pass(id="t1_a")
        t1_b = Pass(id="t1_b")
        t2 = Pass(id="t2")
        (
            wf.start_from_choice(
                [
                    (
                        Var("$.key").is_present()
                        .next_then(t1_a)
                    )
                ],
                id="choice",
                default=t2,
            )
        )
        # you cannot call next_then immediately after creating a choice
        with pytest.raises(exc.WorkflowError):
            wf.next_then(t1_b)

        wf.continue_from(t1_a).next_then(t1_b).end()
        wf.continue_from(t2).end()

        _ = wf.serialize()


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
        "--cov=aws_stepfunction.workflow",
        "--cov-report", "term-missing",
        "--cov-report", f"html:{dir_htmlcov}",
        abspath,
    ]
    subprocess.run(args)
