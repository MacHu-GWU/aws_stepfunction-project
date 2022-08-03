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


class TaskFieldEnum(enum.Enum):
    Resource = "Resource"
    TimeoutSecondsPath = "TimeoutSecondsPath"
    TimeoutSeconds = "TimeoutSeconds"
    HeartbeatSecondsPath = "HeartbeatSecondsPath"
    HeartbeatSeconds = "HeartbeatSeconds"


class ParallelFieldEnum(enum.Enum):
    Branches = "Branches"


class ErrorCodeEnum(enum.Enum):
    """
    Reference:

    - https://states-language.net/spec.html#appendix-a
    """
    AllError = "States.ALL"
    HeartbeatTimeoutError = "States.HeartbeatTimeout"
    TimeoutError = "States.Timeout"
    TaskFailedError = "States.TaskFailed"
    PermissionsError = "States.Permissions"
    ResultPathMatchFailureError = "States.ResultPathMatchFailure"
    ParameterPathFailureError = "States.ParameterPathFailure"
    BranchFailedError = "States.BranchFailed"
    NoChoiceMatchedError = "States.NoChoiceMatched"
    IntrinsicFailureError = "States.IntrinsicFailure"


class RetryFieldEnum(enum.Enum):
    ErrorEquals = "ErrorEquals"
    IntervalSeconds = "IntervalSeconds"
    BackoffRate = "BackoffRate"
    MaxAttempts = "MaxAttempts"


class CatchFieldEnum(enum.Enum):
    ErrorEquals = "ErrorEquals"
    ResultPath = "ResultPath"
    Next = "Next"


class Enum(enum.Enum):
    # Top level field
    States = TopLevelFieldEnum.States.value
    StartAt = TopLevelFieldEnum.StartAt.value
    Comment = TopLevelFieldEnum.Comment.value
    Version = TopLevelFieldEnum.Version.value
    TimeoutSeconds = TopLevelFieldEnum.TimeoutSeconds.value

    # State type
    Task = StateTypeEnum.Task.value
    Parallel = StateTypeEnum.Parallel.value
    Map = StateTypeEnum.Map.value
    Pass = StateTypeEnum.Pass.value
    Wait = StateTypeEnum.Wait.value
    Choice = StateTypeEnum.Choice.value
    Succeed = StateTypeEnum.Succeed.value
    Fail = StateTypeEnum.Fail.value

    # State field
    Type = StateFieldEnum.Type.value
    # Comment = StateFieldEnum.Comment.value
    InputPath = StateFieldEnum.InputPath.value
    OutputPath = StateFieldEnum.OutputPath.value
    Next = StateFieldEnum.Next.value
    End = StateFieldEnum.End.value
    ResultPath = StateFieldEnum.ResultPath.value
    Parameters = StateFieldEnum.Parameters.value
    ResultSelector = StateFieldEnum.ResultSelector.value
    Retry = StateFieldEnum.Retry.value
    Catch = StateFieldEnum.Catch.value

    # Task state field
    Resource = TaskFieldEnum.Resource.value
    TimeoutSecondsPath = TaskFieldEnum.TimeoutSecondsPath.value
    # TimeoutSeconds = TaskFieldEnum.TimeoutSeconds.value
    HeartbeatSecondsPath = TaskFieldEnum.HeartbeatSecondsPath.value
    HeartbeatSeconds = TaskFieldEnum.HeartbeatSeconds.value

    # Parallel state field
    Branches = ParallelFieldEnum.Branches.value

    # Error code
    AllError = ErrorCodeEnum.AllError.value
    HeartbeatTimeoutError = ErrorCodeEnum.HeartbeatTimeoutError.value
    TimeoutError = ErrorCodeEnum.TimeoutError.value
    TaskFailedError = ErrorCodeEnum.TaskFailedError.value
    PermissionsError = ErrorCodeEnum.PermissionsError.value
    ResultPathMatchFailureError = ErrorCodeEnum.ResultPathMatchFailureError.value
    ParameterPathFailureError = ErrorCodeEnum.ParameterPathFailureError.value
    BranchFailedError = ErrorCodeEnum.BranchFailedError.value
    NoChoiceMatchedError = ErrorCodeEnum.NoChoiceMatchedError.value
    IntrinsicFailureError = ErrorCodeEnum.IntrinsicFailureError.value

    # Retry field
    ErrorEquals = RetryFieldEnum.ErrorEquals.value
    IntervalSeconds = RetryFieldEnum.IntervalSeconds.value
    BackoffRate = RetryFieldEnum.BackoffRate.value
    MaxAttempts = RetryFieldEnum.MaxAttempts.value

    # Catch field
    # ErrorEquals = CatchFieldEnum.ErrorEquals.value
    # ResultPath = CatchFieldEnum.ResultPath.value
    # Next = CatchFieldEnum.Next.value
