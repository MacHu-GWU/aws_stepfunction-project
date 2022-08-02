# -*- coding: utf-8 -*-

"""
This is based on https://states-language.net/spec.html
"""

import enum


class TopLevelFieldEnum(enum.Enum):
    States = "States"
    StartAt = "StartAt"
    Comment = "Comment"
    Version = "Version"
    TimeoutSeconds = "TimeoutSeconds"


class StateTypeEnum(enum.Enum):
    Task = "Task"
    Parallel = "Parallel"
    Map = "Map"
    Pass = "Pass"
    Wait = "Wait"
    Choice = "Choice"
    Succeed = "Succeed"
    Fail = "Fail"


class StateFieldEnum(enum.Enum):
    Type = "Type"
    Comment = "Comment"
    InputPath = "InputPath"
    OutputPath = "OutputPath"
    Next = "Next"
    End = "End"
    ResultPath = "ResultPath"
    Parameters = "Parameters"
    ResultSelector = "ResultSelector"
    Retry = "Retry"
    Catch = "Catch"
