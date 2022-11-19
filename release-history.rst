.. _release_history:

Release and Version History
==============================================================================


0.0.5 (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.0.4 (2022-11-19)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add **Magic Task** for better Input/Output handling

**Minor Improvements**

- add better logging
- add support to preview state machine execution

**Miscellaneous**

- more documents


0.0.3 (2022-08-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add the following canned actions:
    - :func:`~aws_stepfunction.actions.aws_lambda.lambda_invoke`
    - :func:`~aws_stepfunction.actions.aws_ecs.ecs_run_task`
    - :func:`~aws_stepfunction.actions.aws_ecs.ecs_start_task`
    - :func:`~aws_stepfunction.actions.aws_ecs.ecs_stop_task`
    - :func:`~aws_stepfunction.actions.aws_batch.batch_submit_job`
    - :func:`~aws_stepfunction.actions.aws_batch.batch_cancel_job`
    - :func:`~aws_stepfunction.actions.aws_batch.batch_terminate_job`
    - :func:`~aws_stepfunction.actions.aws_glue.glue_start_job_run`
    - :func:`~aws_stepfunction.actions.aws_glue.glue_batch_stop_job_run`
    - :func:`~aws_stepfunction.actions.aws_glue.glue_start_crawler`
    - :func:`~aws_stepfunction.actions.aws_glue.glue_stop_crawler`
    - :func:`~aws_stepfunction.actions.aws_sns.sns_publish`
    - :func:`~aws_stepfunction.actions.aws_sns.sns_publish_batch`
    - :func:`~aws_stepfunction.actions.aws_sqs.sqs_send_message`
    - :func:`~aws_stepfunction.actions.aws_sqs.sqs_send_message_batch`


0.0.2 (2022-08-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First usable release
- Add the following to public API:
    - :class:`~aws_stepfunction.state.Task`
    - :class:`~aws_stepfunction.state.Parallel`
    - :class:`~aws_stepfunction.state.Map`
    - :class:`~aws_stepfunction.state.Pass`
    - :class:`~aws_stepfunction.state.Wait`
    - :class:`~aws_stepfunction.state.Choice`
    - :class:`~aws_stepfunction.state.Succeed`
    - :class:`~aws_stepfunction.state.Fail`
    - :class:`~aws_stepfunction.state.Retry`
    - :class:`~aws_stepfunction.state.Catch`
    - :class:`~aws_stepfunction.workflow.Workflow`
    - :class:`~aws_stepfunction.state_machine.StateMachine`
    - :func:`~aws_stepfunction.actions.aws_lambda.lambda_invoke`
    - :func:`~aws_stepfunction.actions.aws_ecs.ecs_run_task`
    - :func:`~aws_stepfunction.actions.aws_glue.glue_start_job_run`
    - :func:`~aws_stepfunction.actions.aws_sns.sns_publish`


0.0.1 (2022-08-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- First release
