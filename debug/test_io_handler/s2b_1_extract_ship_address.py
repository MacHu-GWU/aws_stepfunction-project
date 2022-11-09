# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses


@dataclasses.dataclass
class InputData:
    order_id: str
    items: T.List
    ship_address: str


@dataclasses.dataclass
class OutputData:
    ship_address: str


def lambda_handler(event, context):
    print("received event:")
    print(json.dumps(event, indent=4))
    input = InputData(**event)
    output = OutputData(ship_address=input.ship_address)
    return dataclasses.asdict(output)
