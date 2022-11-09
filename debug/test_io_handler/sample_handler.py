# -*- coding: utf-8 -*-

import json
import dataclasses


@dataclasses.dataclass
class Event:
    """
    :param input:
    :param context: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-contextobject.html
    """
    input: dict = dataclasses.field()
    context: dict = dataclasses.field()


def lambda_handler(event, context):
    print(json.dumps(event, indent=4))
    evt = Event(**event)
    return evt.input
