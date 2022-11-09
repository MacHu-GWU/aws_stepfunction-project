# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses


@dataclasses.dataclass
class Output:
    balance: float


def lambda_handler(
    event: T.Tuple[
        T.Dict[str, float],
        T.Dict[str, float],
    ],
    context,
):
    print("received event:")
    print(json.dumps(event, indent=4))
    total_price = event[0]["total_price"]
    ship_cost = event[1]["ship_cost"]
    output = Output(balance=total_price + ship_cost)
    return dataclasses.asdict(output)
