# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses
import boto3

s3_client = boto3.client("s3")


@dataclasses.dataclass
class Output:
    tasks: T.List[dict]
    status: str


def lambda_handler(event, context):
    print("received event:")
    bucket = "669508176277-us-east-1-data"
    print(json.dumps(event, indent=4))
    res = s3_client.list_objects_v2(
        Bucket=bucket,
        Key="aws_stepfunction/examples/map-pattern/source/",
        MaxKeys=1000,
    )
    tasks = [{"bucket": bucket, "key": dct["Key"]} for dct in res["Contents"]]
    output = Output(tasks=tasks, status="success")
    return dataclasses.asdict(output)
