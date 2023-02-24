import aws_stepfunction as sfn
from boto_session_manager import BotoSesManager
from s3pathlib import S3Path, context
from rich import print as rprint

bsm = BotoSesManager(profile_name="aws_data_lab_sanhe_us_east_1")
context.attach_boto_session(bsm.boto_ses)

bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-data"
s3dir_root = S3Path(bucket, "projects/aws_stepfunction/examples/map-pattern/").to_dir()

def prepare_data():
    s3dir_source = s3dir_root.joinpath("source")
    print(f"preview source data at: {s3dir_source.console_url}")
    n_file = 3
    for ith in range(1, 1+n_file):
        s3path = s3dir_source / f"{ith}.txt"
        s3path.write_text(f"this is the {ith} th file")

# prepare_data()

# ------------------------------------------------------------------------------
task1_coordinator = sfn.LambdaTask(
    id="Task1-Coordinator",
    lbd_func_name="aws_stepfunction_map_pattern-task1_coordinator",
    lbd_package="worker.py",
    lbd_handler="worker.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

task2_worker = sfn.LambdaTask(
    id="Task2-Worker",
    lbd_func_name="aws_stepfunction_map_pattern-task1_worker",
    lbd_package="worker.py",
    lbd_handler="worker.lambda_handler",
    lbd_aws_account_id=bsm.aws_account_id,
    lbd_aws_region=bsm.aws_region,
)

# ------------------------------------------------------------------------------
workflow = sfn.Workflow()
(
    workflow.start_from(task1_coordinator)
    .map(
        (
            workflow.subflow_from(task2_worker)
            .end()
        )
    )
    .end()
)
rprint(workflow.serialize())


# ------------------------------------------------------------------------------
sfn_name = "aws_stepfunction_map_pattern"

state_machine = sfn.StateMachine(
    name=sfn_name,
    workflow=workflow,
    role_arn="arn:aws:iam::669508176277:role/sanhe-for-everything-admin",
)


# ------------------------------------------------------------------------------
state_machine.deploy(bsm=bsm)

