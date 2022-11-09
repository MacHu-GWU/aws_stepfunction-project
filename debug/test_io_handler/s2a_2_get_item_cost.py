# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses


@dataclasses.dataclass
class InputData:
    items: T.List


@dataclasses.dataclass
class OutputData:
    total_price: float


database = {
    "items": {
        1: {"price": 14.99},
        2: {"price": 3.99},
        3: {"price": 7.99},
    }
}


def lambda_handler(event, context):
    print("received event:")
    print(json.dumps(event, indent=4))
    input = InputData(**event)
    total_price = sum([database["items"][item]["price"] for item in input.items])
    output = OutputData(total_price=total_price)
    return dataclasses.asdict(output)
