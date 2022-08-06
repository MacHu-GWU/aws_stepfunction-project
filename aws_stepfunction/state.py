# -*- coding: utf-8 -*-

import typing as T

import attr
import attr.validators as vs

from . import exc
from .constant import (
    Constant as C,
    ErrorCodeEnum,
)
from .utils import short_uuid, is_json_path
from .model import StepFunctionObject
from .choice_rule import ChoiceRule

if T.TYPE_CHECKING:
    from .workflow import Workflow


# ------------------------------------------------------------------------------
# State Data Model
# ------------------------------------------------------------------------------
@attr.s
class State(StepFunctionObject):
    """
    Represent a step / a state in a workflow.

    :param _uuid: for internal implementation. we track the associated
        state machine of each state object.

    Serialization Field Order:

    1. 先展示信息量最大的, 例如 Type, Comment
    2. 再展示跟当前 State 的逻辑紧密相关的, 例如 Task 就需要关注 Resource,
        Parallel 就需要关注 Branches, Map 就需要关注 Iterator 等等
    3. 接下来展示跟流程相关的 Next, End
    4. 最后展示详细的 Input Output 处理的细节
    """
    id: str = attr.ib(
        factory=lambda: short_uuid(),
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default="UnknownState",
        metadata={C.ALIAS: C.Type},
    )
    comment: T.Optional[str] = attr.ib(
        default=None,
        metadata={C.ALIAS: C.Comment},
    )

    def _serialize(self) -> dict:
        data = self.to_dict()
        data = self._to_alias(data)
        data.pop("id")
        if data.get(C.ResultPath, None) == "null":
            data[C.ResultPath] = None
        return data

    # since json path attribute is so common,
    # we should create a validator for that
    def _check_json_path(self, attr: str, value: str):
        if not is_json_path(value):
            raise exc.StateValidationError.make(
                self,
                (
                    f"State.{attr} = {value!r} is not a valid JSON path!"
                )
            )

    def _check_opt_json_path(self, attr: str, value: T.Optional[str]):
        if value is not None:
            self._check_json_path(attr, value)


@attr.s
class _HasNextOrEnd(State):
    next: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.Next}
    )
    end: T.Optional[bool] = attr.ib(
        default=None, metadata={C.ALIAS: C.End}
    )

    def _check_next_and_end(self):
        if self.end is True:
            if self.next:
                # when "End" is True, you can NOT have "Next"
                raise exc.StateValidationError.make(
                    self,
                    f"{C.End!r} is True, "
                    f"but the {C.Next!r} is also defined!"
                )
        else:
            if not self.next:
                # when "End" is not True, you HAVE TO have "Next"
                raise exc.StateValidationError.make(
                    self,
                    f"{C.End!r} is False, "
                    f"but the {C.Next!r} is not defined!"
                )


@attr.s
class _HasInputOutput(State):
    input_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.InputPath},
    )
    output_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.OutputPath},
    )

    def _check_input_output_path(self):
        self._check_opt_json_path(C.InputPath, self.input_path)
        self._check_opt_json_path(C.OutputPath, self.output_path)


@attr.s
class _HasParameters(State):
    parameters: T.Dict[str, T.Any] = attr.ib(
        factory=dict, metadata={C.ALIAS: C.Parameters},
    )


@attr.s
class _HasResultSelector(State):
    result_selector: T.Dict[str, T.Any] = attr.ib(
        factory=dict, metadata={C.ALIAS: C.ResultSelector},
    )


@attr.s
class _HasResultPath(State):
    result_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.ResultPath},
    )

    def _check_result_path(self):
        if self.result_path is not None:
            if self.result_path != "null":
                self._check_json_path(C.ResultPath, self.result_path)

    def use_task_result(self) -> T.Union[
        'Task', 'Parallel', 'Map', 'Pass'
    ]:
        self.result_path = "$"
        return self

    def discard_the_result_and_keep_original_input(self) -> T.Union[
        'Task', 'Parallel', 'Map', 'Pass'
    ]:
        self.result_path = "null"
        return self


@attr.s
class _RetryOrCatch(StepFunctionObject):
    error_equals: T.List[str] = attr.ib(
        factory=list, metadata={C.ALIAS: C.ErrorEquals},
    )

    @classmethod
    def new(cls) -> '_RetryOrCatch':
        return cls()

    def _check_error_codes(self):
        if len(self.error_equals) == 0:
            raise exc.StateValidationError(
                f"{C.ErrorEquals!r} has to be a NON EMPTY list!"
            )
        for error_code in self.error_equals:
            if not ErrorCodeEnum.contains(error_code):
                raise exc.StateValidationError(
                    f"{error_code!r} is not a valid Error Code!"
                )

    def _add_error(self, error_code: str) -> '_RetryOrCatch':
        if error_code not in self.error_equals:
            self.error_equals.append(error_code)
        return self

    def if_all_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.AllError.value)

    def if_heartbeat_timeout_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.HeartbeatTimeoutError.value)

    def if_timeout_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.TimeoutError.value)

    def if_task_failed_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.TaskFailedError.value)

    def if_permissions_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.PermissionsError.value)

    def if_result_path_match_failure_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.ResultPathMatchFailureError.value)

    def if_parameter_path_failure_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.ParameterPathFailureError.value)

    def if_branch_failed_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.BranchFailedError.value)

    def if_no_choice_matched_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.NoChoiceMatchedError.value)

    def if_intrinsic_failure_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.IntrinsicFailureError.value)

    def if_data_limit_exceeded_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.DataLimitExceededError.value)

    def if_lambda_unknown_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.LambdaUnknownError.value)

    def if_lambda_service_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.LambdaServiceError.value)

    def if_lambda_aws_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.LambdaAWSError.value)

    def if_lambda_sdk_client_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.LambdaSdkClientError.value)

    def if_lambda_too_many_requests_error(self) -> '_RetryOrCatch':
        return self._add_error(ErrorCodeEnum.LambdaTooManyRequestsError.value)

    def _serialize(self) -> dict:
        data = self.to_dict()
        data = self._to_alias(data)
        return data


@attr.s
class Retry(_RetryOrCatch):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html#error-handling-retrying-after-an-error
    """
    interval_seconds: T.Optional[int] = attr.ib(
        default=None, metadata={C.ALIAS: C.IntervalSeconds},
    )
    backoff_rate: T.Optional[T.Union[float, int]] = attr.ib(
        default=None, metadata={C.ALIAS: C.BackoffRate},
    )
    max_attempts: T.Optional[int] = attr.ib(
        default=None, metadata={C.ALIAS: C.MaxAttempts},
    )

    def with_interval_seconds(self, sec: int) -> 'Retry':
        self.interval_seconds = sec
        return self

    def with_back_off_rate(self, rate: T.Union[float, int]) -> 'Retry':
        self.backoff_rate = rate
        return self

    def with_max_attempts(self, attempts: int) -> 'Retry':
        self.max_attempts = attempts
        return self

    def _pre_serialize_validation(self):
        self._check_error_codes()


@attr.s
class Catch(_RetryOrCatch):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html#error-handling-fallback-states
    """
    next: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.Next},
    )
    result_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.ResultPath},
    )

    def next_then(self, state: 'StateType'):
        self.next = state.id
        return self

    def with_result_path(self, result_path: str):
        """
        A path that determines what input is sent to the state specified
        in the Next field.
        """
        self.result_path = result_path
        return self

    def _check_next(self):
        if self.next is None:
            raise exc.ValidationError(f"{C.Catch}.{C.Next} is not defined!")

    def _check_result(self):
        if self.result_path is not None:
            if not is_json_path(self.result_path):
                raise exc.ValidationError(
                    f"{C.Catch}.{C.ResultPath} = {self.result_path!r} "
                    f"is not a valid JSON path!"
                )

    def _pre_serialize_validation(self):
        self._check_error_codes()
        self._check_next()


@attr.s
class _HasRetryCatch(State):
    retry: T.List['Retry'] = attr.ib(
        factory=list, metadata={C.ALIAS: C.Retry},
    )
    catch: T.List['Catch'] = attr.ib(
        factory=list, metadata={C.ALIAS: C.Catch},
    )

    def _serialize_retry_catch_fields(self, data: dict) -> dict:
        if self.retry:
            data[C.Retry] = [
                retry.serialize()
                for retry in self.retry
            ]

        if self.catch:
            data[C.Catch] = [
                catch.serialize()
                for catch in self.catch
            ]

        return data


@attr.s
class Task(
    _HasNextOrEnd,
    _HasInputOutput,
    _HasParameters,
    _HasResultSelector,
    _HasResultPath,
    _HasRetryCatch,
):
    id: str = attr.ib(
        factory=lambda: f"{C.Task}-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default=C.Task, metadata={C.ALIAS: C.Type},
    )
    resource: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.Resource},
    )
    timeout_seconds_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.TimeoutSecondsPath},
    )
    timeout_seconds: T.Optional[int] = attr.ib(
        default=None, metadata={C.ALIAS: C.TimeoutSeconds},
    )
    heartbeat_seconds_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.HeartbeatSecondsPath},
    )
    heartbeat_seconds: T.Optional[int] = attr.ib(
        default=None, metadata={C.ALIAS: C.HeartbeatSeconds},
    )

    _se_order = [
        # common
        C.Type,
        C.Comment,
        # state specific
        C.Resource,
        C.TimeoutSeconds,
        C.TimeoutSecondsPath,
        C.HeartbeatSeconds,
        C.HeartbeatSecondsPath,
        # flow
        C.Next,
        C.End,
        # input output
        C.InputPath,
        C.Parameters,
        C.ResultSelector,
        C.ResultPath,
        C.OutputPath,
        # error handling
        C.Retry,
        C.Catch,
    ]

    def update(
        self,
        id: T.Optional[str] = None,
        resource: T.Optional[str] = None,
        timeout_seconds_path: T.Optional[str] = None,
        timeout_seconds: T.Optional[int] = None,
        heartbeat_seconds_path: T.Optional[str] = None,
        heartbeat_seconds: T.Optional[int] = None,
        next: T.Optional[str] = None,
        end: T.Optional[bool] = None,
        input_path: T.Optional[str] = None,
        output_path: T.Optional[str] = None,
        parameters: T.Optional[str] = None,
        result_selector: T.Optional[str] = None,
        result_path: T.Optional[str] = None,
        retry: T.Optional[T.List['Retry']] = None,
        catch: T.Optional[T.List['Catch']] = None,
    ):
        for attr, value in [
            ("id", id),
            ("resource", resource),
            ("timeout_seconds_path", timeout_seconds_path),
            ("timeout_seconds", timeout_seconds),
            ("heartbeat_seconds_path", heartbeat_seconds_path),
            ("heartbeat_seconds", heartbeat_seconds),
            ("next", next),
            ("end", end),
            ("input_path", input_path),
            ("output_path", output_path),
            ("parameters", parameters),
            ("result_selector", result_selector),
            ("result_path", result_path),
            ("retry", retry),
            ("catch", catch),
        ]:
            if value is not None:
                setattr(self, attr, value)
        return self

    def _check_resource(self):
        if self.resource is None:
            raise exc.StateValidationError.make(
                self,
                f"{C.Resource!r} is not defined!"
            )

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()
        self._check_result_path()

        self._check_resource()
        self._check_opt_json_path(C.TimeoutSecondsPath, self.timeout_seconds_path)
        self._check_opt_json_path(C.HeartbeatSecondsPath, self.heartbeat_seconds_path)

    def _serialize(self) -> dict:
        data = super()._serialize()
        data = self._serialize_retry_catch_fields(data)
        return data


@attr.s
class Parallel(
    _HasNextOrEnd,
    _HasInputOutput,
    _HasParameters,
    _HasResultSelector,
    _HasResultPath,
    _HasRetryCatch,
):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-parallel-state.html
    """
    id: str = attr.ib(
        factory=lambda: f"{C.Parallel}-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default=C.Parallel, metadata={C.ALIAS: C.Type},
    )
    branches: T.List['Workflow'] = attr.ib(
        factory=list, metadata={C.ALIAS: C.Branches},
    )

    _se_order = [
        # common
        # state specific
        # flow
        # input output
        # error handling
        C.Type,
        C.Comment,

        C.Branches,

        C.Next,
        C.End,

        C.InputPath,
        C.Parameters,
        C.ResultSelector,
        C.ResultPath,
        C.OutputPath,

        C.Retry,
        C.Catch,
    ]

    def _check_branches(self):
        if len(self.branches) == 0:
            raise exc.StateValidationError(
                f"{C.Parallel!r} state can not have empty {C.Branches!r}!"
            )

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()
        self._check_result_path()

        self._check_branches()

    def _serialize(self) -> dict:
        data = super()._serialize()
        data = self._serialize_retry_catch_fields(data)
        branches = list()
        for state_machine in self.branches:
            dct = state_machine.serialize()
            branches.append(dct)
        data[C.Branches] = branches
        return data


@attr.s
class Map(
    _HasNextOrEnd,
    _HasInputOutput,
    _HasParameters,
    _HasResultSelector,
    _HasResultPath,
    _HasRetryCatch,
):
    id: str = attr.ib(
        factory=lambda: f"{C.Map}-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default=C.Map, metadata={C.ALIAS: C.Type},
    )

    iterator: T.Optional['Workflow'] = attr.ib(
        default=None, metadata={C.ALIAS: C.Iterator},
    )
    items_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.ItemsPath},
    )
    max_concurrency: T.Optional[int] = attr.ib(
        default=None, metadata={C.ALIAS: C.MaxConcurrency},
    )

    _se_order = [
        # common
        C.Type,
        C.Comment,
        # state specific
        C.Iterator,
        C.ItemsPath,
        C.MaxConcurrency,
        # flow
        C.Next,
        C.End,
        # input output
        C.InputPath,
        C.Parameters,
        C.ResultSelector,
        C.ResultPath,
        C.OutputPath,
        # error handling

        C.Retry,
        C.Catch,
    ]

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()
        self._check_result_path()

        self._check_opt_json_path(C.ItemsPath, self.items_path)

    def _serialize(self) -> dict:
        data = super()._serialize()
        data = self._serialize_retry_catch_fields(data)
        data[C.Iterator] = self.iterator.serialize()
        return data


@attr.s
class Pass(
    _HasInputOutput,
    _HasNextOrEnd,
    _HasResultPath,
    _HasParameters,
):
    id: str = attr.ib(
        factory=lambda: f"{C.Pass.value}-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default=C.Pass, metadata={C.ALIAS: C.Type},
    )

    _se_order = [
        # common
        C.Type,
        C.Comment,
        # flow
        C.Next,
        C.End,
        # input output
        C.InputPath,
        C.Parameters,
        C.ResultPath,
        C.OutputPath,
    ]

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()
        self._check_result_path()


@attr.s
class Wait(
    _HasInputOutput,
    _HasNextOrEnd,
):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-wait-state.html
    """
    id: str = attr.ib(
        factory=lambda: f"{C.Wait}-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default=C.Wait, metadata={C.ALIAS: C.Type},
    )

    seconds: T.Optional[int] = attr.ib(
        default=None, metadata={C.ALIAS: C.Seconds},
    )
    timestamp: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.Timestamp},
    )
    seconds_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.SecondsPath},
    )
    timestamp_path: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.TimestampPath},
    )

    _se_order = [
        # common
        C.Type,
        C.Comment,
        # state specific
        C.Seconds,
        C.Timestamp,
        C.SecondsPath,
        C.TimestampPath,
        # flow
        C.Next,
        C.End,
        # input output
        C.InputPath,
        C.OutputPath,
    ]

    def _pre_serialize_validation(self):
        self._check_next_and_end()
        self._check_input_output_path()


@attr.s
class Choice(
    _HasInputOutput
):
    """
    Reference:

    - https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-choice-state.html
    """
    id: str = attr.ib(
        factory=lambda: f"{C.Choice}-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default=C.Choice, metadata={C.ALIAS: C.Type},
    )

    choices: T.List['ChoiceRule'] = attr.ib(
        factory=list, metadata={C.ALIAS: C.Choices},
    )
    default: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.Default},
    )

    _se_order = [
        # common
        C.Type,
        C.Comment,
        # state specific
        C.Choices,
        C.Default,
        # input output
        C.InputPath,
        C.OutputPath,
    ]

    def _check_choices(self):
        if len(self.choices) == 0:
            raise exc.StateValidationError

    def _pre_serialize_validation(self):
        self._check_input_output_path()

        self._check_choices()

    def default_succeed(
        self,
        id: T.Optional[str] = None
    ) -> 'Succeed':
        """
        """
        kwargs = dict()
        if id is not None:
            kwargs["id"] = id
        succeed = Succeed(**kwargs)
        self.default = succeed.id
        return succeed

    def default_fail(
        self,
        id: T.Optional[str] = None,
        cause: T.Optional[str] = None,
        error: T.Optional[str] = None,
    ) -> 'Fail':
        """
        """
        kwargs = dict(cause=cause, error=error)
        if id is not None:
            kwargs["id"] = id
        fail = Fail(**kwargs)
        self.default = fail.id
        return fail

    def _serialize(self) -> dict:
        data = super()._serialize()
        choices = [
            choice.serialize()
            for choice in self.choices
        ]
        data[C.Choices] = choices
        return data


@attr.s
class Succeed(
    _HasInputOutput,
):
    id: str = attr.ib(
        factory=lambda: f"{C.Succeed}-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default=C.Succeed, metadata={C.ALIAS: C.Type},
    )

    _se_order = [
        # common
        C.Type,
        C.Comment,
        # input output
        C.InputPath,
        C.OutputPath,
    ]

    def _pre_serialize_validation(self):
        self._check_input_output_path()


@attr.s
class Fail(
    State,
):
    id: str = attr.ib(
        factory=lambda: f"{C.Fail}-{short_uuid()}",
        validator=vs.instance_of(str),
    )
    type: str = attr.ib(
        default=C.Fail, metadata={C.ALIAS: C.Type},
    )

    cause: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.Cause},
    )
    error: T.Optional[str] = attr.ib(
        default=None, metadata={C.ALIAS: C.Error},
    )

    _se_order = [
        # common
        C.Type,
        C.Comment,
        # state specific
        C.Cause,
        C.Error,
    ]


StateType = T.Union[
    Task,
    Parallel,
    Map,
    Pass,
    Wait,
    Choice,
    Succeed,
    Fail,
]
