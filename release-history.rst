.. _release_history:

Release and Version History
==============================================================================


0.0.4 (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.0.3 (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add the following canned actions:
    - :func:`~aws_stepfunction.actions.lambda_invoke`
    - :func:`~aws_stepfunction.actions.ecs_run_task`
    - :func:`~aws_stepfunction.actions.ecs_start_task`
    - :func:`~aws_stepfunction.actions.ecs_stop_task`
    - :func:`~aws_stepfunction.actions.batch_submit_job`
    - :func:`~aws_stepfunction.actions.batch_cancel_job`
    - :func:`~aws_stepfunction.actions.batch_terminate_job`
    - :func:`~aws_stepfunction.actions.glue_start_job_run`
    - :func:`~aws_stepfunction.actions.glue_batch_stop_job_run`
    - :func:`~aws_stepfunction.actions.glue_start_crawler`
    - :func:`~aws_stepfunction.actions.glue_stop_crawler`
    - :func:`~aws_stepfunction.actions.sns_publish`
    - :func:`~aws_stepfunction.actions.sns_publish_batch`
    - :func:`~aws_stepfunction.actions.sqs_send_message`
    - :func:`~aws_stepfunction.actions.sqs_send_message_batch`


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
    - :func:`~aws_stepfunction.actions.base.lambda_invoke`
    - :func:`~aws_stepfunction.actions.base.ecs_run_task`
    - :func:`~aws_stepfunction.actions.base.glue_start_job_run`
    - :func:`~aws_stepfunction.actions.base.sns_publish`


0.0.1 (2022-08-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- First release
