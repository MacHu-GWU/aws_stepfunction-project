# -*- coding: utf-8 -*-

"""
This is based on https://states-language.net/spec.html
"""

from enum import Enum


class StringEnum(Enum):
    @classmethod
    def contains(cls, value: str) -> bool:
        return value in cls._value2member_map_


class TopLevelFieldEnum(StringEnum):
    States = "States"
    StartAt = "StartAt"
    Comment = "Comment"
    Version = "Version"
    TimeoutSeconds = "TimeoutSeconds"


class StateTypeEnum(StringEnum):
    Task = "Task"
    Parallel = "Parallel"
    Map = "Map"
    Pass = "Pass"
    Wait = "Wait"
    Choice = "Choice"
    Succeed = "Succeed"
    Fail = "Fail"


class StateFieldEnum(StringEnum):
    ID = "ID"
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


class TaskFieldEnum(StringEnum):
    Resource = "Resource"
    TimeoutSecondsPath = "TimeoutSecondsPath"
    TimeoutSeconds = "TimeoutSeconds"
    HeartbeatSecondsPath = "HeartbeatSecondsPath"
    HeartbeatSeconds = "HeartbeatSeconds"


class ParallelFieldEnum(StringEnum):
    Branches = "Branches"


class MapFieldEnum(StringEnum):
    Iterator = "Iterator"
    ItemsPath = "ItemsPath"
    MaxConcurrency = "MaxConcurrency"


class PassFieldEnum(StringEnum):
    Result = "Result"


class WaitFieldEnum(StringEnum):
    Seconds = "Seconds"
    Timestamp = "Timestamp"
    SecondsPath = "SecondsPath"
    TimestampPath = "TimestampPath"


class ChoiceFieldEnum(StringEnum):
    Choices = "Choices"
    Default = "Default"


class SucceedFieldEnum(StringEnum):
    pass


class FailFieldEnum(StringEnum):
    Cause = "Cause"
    Error = "Error"


class ErrorCodeEnum(StringEnum):
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

    DataLimitExceededError = "States.DataLimitExceeded"

    LambdaUnknownError = "Lambda.Unknown"
    LambdaServiceError = "Lambda.ServiceException"
    LambdaAWSError = "Lambda.AWSLambdaException"
    LambdaSdkClientError = "Lambda.SdkClientException"
    LambdaTooManyRequestsError = "Lambda.TooManyRequestsException"


class RetryFieldEnum(StringEnum):
    ErrorEquals = "ErrorEquals"
    IntervalSeconds = "IntervalSeconds"
    BackoffRate = "BackoffRate"
    MaxAttempts = "MaxAttempts"


class CatchFieldEnum(StringEnum):
    ErrorEquals = "ErrorEquals"
    ResultPath = "ResultPath"
    Next = "Next"


class TestFieldEnum(StringEnum):
    Variable = "Variable"


class LogicOperatorEnum(StringEnum):
    """
    Reference:

    - https://states-language.net/spec.html#choice-state,
        the "Boolean expression" section
    """
    And = "And"
    Or = "Or"
    Not = "Not"


class TestExpressionEnum(StringEnum):
    """
    Reference:

    - https://states-language.net/spec.html#choice-state,
        the "Data-test expression" section
    """
    IsBoolean = "IsBoolean"
    IsNull = "IsNull"
    IsNumeric = "IsNumeric"
    IsPresent = "IsPresent"
    IsString = "IsString"
    IsTimestamp = "IsTimestamp"
    NumericEquals = "NumericEquals"
    NumericEqualsPath = "NumericEqualsPath"
    NumericGreaterThan = "NumericGreaterThan"
    NumericGreaterThanEquals = "NumericGreaterThanEquals"
    NumericGreaterThanEqualsPath = "NumericGreaterThanEqualsPath"
    NumericGreaterThanPath = "NumericGreaterThanPath"
    NumericLessThan = "NumericLessThan"
    NumericLessThanEquals = "NumericLessThanEquals"
    NumericLessThanEqualsPath = "NumericLessThanEqualsPath"
    NumericLessThanPath = "NumericLessThanPath"
    StringEquals = "StringEquals"
    StringEqualsPath = "StringEqualsPath"
    StringGreaterThan = "StringGreaterThan"
    StringGreaterThanEquals = "StringGreaterThanEquals"
    StringGreaterThanEqualsPath = "StringGreaterThanEqualsPath"
    StringGreaterThanPath = "StringGreaterThanPath"
    StringLessThan = "StringLessThan"
    StringLessThanEquals = "StringLessThanEquals"
    StringLessThanEqualsPath = "StringLessThanEqualsPath"
    StringLessThanPath = "StringLessThanPath"
    StringMatches = "StringMatches"
    BooleanEquals = "BooleanEquals"
    BooleanEqualsPath = "BooleanEqualsPath"
    TimestampEquals = "TimestampEquals"
    TimestampEqualsPath = "TimestampEqualsPath"
    TimestampGreaterThan = "TimestampGreaterThan"
    TimestampGreaterThanEquals = "TimestampGreaterThanEquals"
    TimestampGreaterThanEqualsPath = "TimestampGreaterThanEqualsPath"
    TimestampGreaterThanPath = "TimestampGreaterThanPath"
    TimestampLessThan = "TimestampLessThan"
    TimestampLessThanEquals = "TimestampLessThanEquals"
    TimestampLessThanEqualsPath = "TimestampLessThanEqualsPath"
    TimestampLessThanPath = "TimestampLessThanPath"


class Constant:
    # --- Top level field
    States = TopLevelFieldEnum.States.value
    StartAt = TopLevelFieldEnum.StartAt.value
    Comment = TopLevelFieldEnum.Comment.value
    Version = TopLevelFieldEnum.Version.value
    TimeoutSeconds = TopLevelFieldEnum.TimeoutSeconds.value

    # --- State type
    Task = StateTypeEnum.Task.value
    Parallel = StateTypeEnum.Parallel.value
    Map = StateTypeEnum.Map.value
    Pass = StateTypeEnum.Pass.value
    Wait = StateTypeEnum.Wait.value
    Choice = StateTypeEnum.Choice.value
    Succeed = StateTypeEnum.Succeed.value
    Fail = StateTypeEnum.Fail.value

    # --- State field
    ID = StateFieldEnum.ID.value
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

    # --- Task state field
    Resource = TaskFieldEnum.Resource.value
    TimeoutSecondsPath = TaskFieldEnum.TimeoutSecondsPath.value
    # TimeoutSeconds = TaskFieldEnum.TimeoutSeconds.value
    HeartbeatSecondsPath = TaskFieldEnum.HeartbeatSecondsPath.value
    HeartbeatSeconds = TaskFieldEnum.HeartbeatSeconds.value

    # --- Parallel state field
    Branches = ParallelFieldEnum.Branches.value

    # --- Map state field
    Iterator = MapFieldEnum.Iterator.value
    ItemsPath = MapFieldEnum.ItemsPath.value
    MaxConcurrency = MapFieldEnum.MaxConcurrency.value

    # --- Pass state field
    Result = PassFieldEnum.Result.value

    # --- Wait state field
    Seconds = WaitFieldEnum.Seconds.value
    Timestamp = WaitFieldEnum.Timestamp.value
    SecondsPath = WaitFieldEnum.SecondsPath.value
    TimestampPath = WaitFieldEnum.TimestampPath.value

    # --- Choice state field
    Choices = ChoiceFieldEnum.Choices.value
    Default = ChoiceFieldEnum.Default.value

    # --- Succeed state field

    # --- Fail state field
    Cause = FailFieldEnum.Cause.value
    Error = FailFieldEnum.Error.value

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
    DataLimitExceededError = ErrorCodeEnum.DataLimitExceededError.value

    LambdaUnknownError = ErrorCodeEnum.LambdaUnknownError.value
    LambdaServiceError = ErrorCodeEnum.LambdaServiceError.value
    LambdaAWSError = ErrorCodeEnum.LambdaAWSError.value
    LambdaSdkClientError = ErrorCodeEnum.LambdaSdkClientError.value
    LambdaTooManyRequestsError = ErrorCodeEnum.LambdaTooManyRequestsError.value

    # Retry field
    ErrorEquals = RetryFieldEnum.ErrorEquals.value
    IntervalSeconds = RetryFieldEnum.IntervalSeconds.value
    BackoffRate = RetryFieldEnum.BackoffRate.value
    MaxAttempts = RetryFieldEnum.MaxAttempts.value

    # --- Catch field
    # ErrorEquals = CatchFieldEnum.ErrorEquals.value
    # ResultPath = CatchFieldEnum.ResultPath.value
    # Next = CatchFieldEnum.Next.value

    # --- Logic Operator
    And = LogicOperatorEnum.And.value
    Or = LogicOperatorEnum.Or.value
    Not = LogicOperatorEnum.Not.value

    # --- Test Expression
    Variable = TestFieldEnum.Variable.value

    IsBoolean = TestExpressionEnum.IsBoolean.value
    IsNull = TestExpressionEnum.IsNull.value
    IsNumeric = TestExpressionEnum.IsNumeric.value
    IsPresent = TestExpressionEnum.IsPresent.value
    IsString = TestExpressionEnum.IsString.value
    IsTimestamp = TestExpressionEnum.IsTimestamp.value

    StringMatches = TestExpressionEnum.StringMatches.value

    NumericEquals = TestExpressionEnum.NumericEquals.value
    NumericEqualsPath = TestExpressionEnum.NumericEqualsPath.value
    NumericGreaterThan = TestExpressionEnum.NumericGreaterThan.value
    NumericGreaterThanPath = TestExpressionEnum.NumericGreaterThanPath.value
    NumericGreaterThanEquals = TestExpressionEnum.NumericGreaterThanEquals.value
    NumericGreaterThanEqualsPath = TestExpressionEnum.NumericGreaterThanEqualsPath.value
    NumericLessThan = TestExpressionEnum.NumericLessThan.value
    NumericLessThanPath = TestExpressionEnum.NumericLessThanPath.value
    NumericLessThanEquals = TestExpressionEnum.NumericLessThanEquals.value
    NumericLessThanEqualsPath = TestExpressionEnum.NumericLessThanEqualsPath.value
    StringEquals = TestExpressionEnum.StringEquals.value
    StringEqualsPath = TestExpressionEnum.StringEqualsPath.value
    StringGreaterThan = TestExpressionEnum.StringGreaterThan.value
    StringGreaterThanPath = TestExpressionEnum.StringGreaterThanPath.value
    StringGreaterThanEquals = TestExpressionEnum.StringGreaterThanEquals.value
    StringGreaterThanEqualsPath = TestExpressionEnum.StringGreaterThanEqualsPath.value
    StringLessThan = TestExpressionEnum.StringLessThan.value
    StringLessThanPath = TestExpressionEnum.StringLessThanPath.value
    StringLessThanEquals = TestExpressionEnum.StringLessThanEquals.value
    StringLessThanEqualsPath = TestExpressionEnum.StringLessThanEqualsPath.value
    BooleanEquals = TestExpressionEnum.BooleanEquals.value
    BooleanEqualsPath = TestExpressionEnum.BooleanEqualsPath.value
    TimestampEquals = TestExpressionEnum.TimestampEquals.value
    TimestampEqualsPath = TestExpressionEnum.TimestampEqualsPath.value
    TimestampGreaterThan = TestExpressionEnum.TimestampGreaterThan.value
    TimestampGreaterThanPath = TestExpressionEnum.TimestampGreaterThanPath.value
    TimestampGreaterThanEquals = TestExpressionEnum.TimestampGreaterThanEquals.value
    TimestampGreaterThanEqualsPath = TestExpressionEnum.TimestampGreaterThanEqualsPath.value
    TimestampLessThan = TestExpressionEnum.TimestampLessThan.value
    TimestampLessThanPath = TestExpressionEnum.TimestampLessThanPath.value
    TimestampLessThanEquals = TestExpressionEnum.TimestampLessThanEquals.value
    TimestampLessThanEqualsPath = TestExpressionEnum.TimestampLessThanEqualsPath.value

    # Python library implementation constant
    Sep = "____"
    ALIAS = "alias"
