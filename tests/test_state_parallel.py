# -*- coding: utf-8 -*-

import os
import pytest
from rich import print as rprint

from aws_stepfunction import exc
from aws_stepfunction.workflow import Workflow
from aws_stepfunction.state import Task, Parallel
from aws_stepfunction.constant import Constant as C


# class TestParallel:
#     def test_init_directly(self):
#         with Workflow(is_parallel_branch=True) as sm1:
#             task21 = Task(id="task21", resource="arn", end=True)
#             sm1.set_start_at(task21)
#
#         with Workflow(is_parallel_branch=True) as sm2:
#             task22 = Task(id="task22", resource="arn", end=True)
#             sm2.set_start_at(task22)
#
#         para = Parallel(branches=[sm1, sm2])
#
#         with pytest.raises(exc.StateValidationError):
#             para.serialize()
#
#         para.end = True
#         assert para.serialize() == {
#             C.Type: C.Parallel,
#             C.Branches: [
#                 {
#                     C.StartAt: task21.id,
#                     C.States: {
#                         task21.id: task21.serialize()
#                     }
#                 },
#                 {
#                     C.StartAt: task22.id,
#                     C.States: {
#                         task22.id: task22.serialize()
#                     }
#                 }
#             ],
#             C.End: True
#         }

    # def test_init_from_task(self):
    #     with StateMachine() as sm:
    #
    #         task1 = Task(ID="task1", Resource="arn")
    #         task21 = Task(ID="task21", Resource="arn")
    #         task22 = Task(ID="task22", Resource="arn")
    #         task3 = Task(ID="task3", Resource="arn")
    #
    #         (
    #             task1
    #             .parallel([task21, task22])
    #             .next(task3)
    #             .end()
    #         )
    #
    #         sm.set_start_at(task1)
    #
    #     # rprint(sm.serialize())
    #
    #     print(sm._state_orders)


if __name__ == "__main__":
    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
