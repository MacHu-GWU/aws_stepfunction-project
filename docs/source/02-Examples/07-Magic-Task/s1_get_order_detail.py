# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses


@dataclasses.dataclass
class InputData:
    order_id: str


database = {
    "orders": {
        "order-1": {
            "order_id": "order-1",
            "items": [1, 2],
            "ship_address": "123 st, Newyork, NY 10001",
        },
        "order-2": {"..."},
        "order-3": {"..."},
    }
}


@dataclasses.dataclass
class OutputData:
    order_id: str
    items: T.List
    ship_address: str


def lambda_handler(event, context):
    print("received event:")
    print(json.dumps(event, indent=4))
    input = InputData(**event)
    output = OutputData(**database["orders"][input.order_id])
    return dataclasses.asdict(output)
