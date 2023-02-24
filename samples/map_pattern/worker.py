# -*- coding: utf-8 -*-

import json
import dataclasses
import boto3

s3_client = boto3.client("s3")


@dataclasses.dataclass
class Input:
    bucket: str
    key: str


@dataclasses.dataclass
class Output:
    status: str


def lambda_handler(event, context):
    print("received event:")
    print(json.dumps(event, indent=4))
    input = Input(**event)
    try:
        s3_client.copy_object(
            Bucket=input.bucket,
            Key=input.key + ".backup",
            CopySource={"Bucket": input.bucket, "Key": input.key},
        )
        output = Output(status="success")
    except:
        output = Output(status="failed")
    return dataclasses.asdict(output)
