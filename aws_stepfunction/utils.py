# -*- coding: utf-8 -*-

import uuid
import hashlib


def short_uuid(n: int = 7) -> str:
    """
    return short uuid.
    """
    m = hashlib.sha1()
    m.update(uuid.uuid4().bytes)
    return m.hexdigest()[:n]


def is_json_path(path: str):
    if not path.startswith("$."):
        raise ValueError
