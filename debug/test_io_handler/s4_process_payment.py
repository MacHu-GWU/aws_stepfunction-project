# -*- coding: utf-8 -*-

import json
import dataclasses


@dataclasses.dataclass
class Input:
    balance: float


def charge_credit_card(card_number: str, balance: float):
    pass


@dataclasses.dataclass
class Output:
    status: str


def lambda_handler(event, context):
    print("received event:")
    print(json.dumps(event, indent=4))
    input = Input(**event)
    try:
        charge_credit_card("1234-5678-1234-5678", input.balance)
        output = Output(status="success")
    except:
        output = Output(status="failed")
    return dataclasses.asdict(output)
