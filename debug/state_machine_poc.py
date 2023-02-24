# -*- coding: utf-8 -*-

from aws_stepfunction.workflow import Workflow
from aws_stepfunction.state import Task
from aws_stepfunction.choice_rule import Var


def make_task(id: str) -> Task:
    return Task(id=id)


sm = Workflow()

t01 = Task(ID="T01", Resource="arn")
t02 = Task(ID="T02", Resource="arn")
t03_a1 = Task(ID="T03-a1", Resource="arn")
t03_a2 = Task(ID="T03-a2", Resource="arn")
t03_b1 = Task(ID="T03-b1", Resource="arn")
t03_b2 = Task(ID="T03-b2", Resource="arn")
t03_c = Task(ID="T03-c", Resource="arn")
t04 = Task(ID="T04", Resource="arn")
t05_a1 = Task(ID="T05-a1", Resource="arn")
t05_a2 = Task(ID="T05-a2", Resource="arn")
t05_b1 = Task(ID="T05-b1", Resource="arn")
t05_b2 = Task(ID="T05-b2", Resource="arn")
t06 = Task(ID="T06", Resource="arn")
t07 = Task(ID="T07", Resource="arn")
t08 = Task(ID="T08", Resource="arn")
t09 = Task(ID="T09", Resource="arn")
t10 = Task(ID="T10", Resource="arn")

(
    sm._start_at(t01)
    .next_then(t02)
    .choice([
        (
            Var("$.key").string_equals("v1")
            .next(t03_a1)
            .next_then(t03_a2)
            .next_then(t04)
        ),
        (
            Var("$.key").string_equals("v2")
            .next(t03_b1)
            .next_then(t03_b2)
            .next_then(t04)
        ),
        (
            Var("$.key").string_equals("v2")
            .next(t03_b1)
            .next_then(t03_b2)
            .next_then(t04)
        )
    ])
    .default_fail()
)

(
    sm.continue_from(t04)
    .parallel([
        t05_a1.next(t05_a2).end(),
        t05_b1.next(t05_b2).end(),
    ])
    .next_then(t06)
    .wait(
        seconds=10,
    )
    .next_then(t07)
    .map(
        t08.next(t09),
        items_path="$.items",
    )
    .next_then(t10)
    .end()
)
