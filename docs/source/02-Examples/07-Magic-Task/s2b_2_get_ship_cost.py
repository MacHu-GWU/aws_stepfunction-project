# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses


@dataclasses.dataclass
class InputData:
    ship_address: str


@dataclasses.dataclass
class OutputData:
    ship_cost: float


def lambda_handler(event, context):
    print("received event:")
    print(json.dumps(event, indent=4))
    input = InputData(**event)
    output = OutputData(ship_cost=9.99)
    return dataclasses.asdict(output)
