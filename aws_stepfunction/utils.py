# -*- coding: utf-8 -*-

"""
Utility functions.
"""

import uuid
import hashlib


def short_uuid(n: int = 7) -> str:
    """
    return short uuid.
    """
    m = hashlib.sha1()
    m.update(uuid.uuid4().bytes)
    return m.hexdigest()[:n]


def is_json_path(path: str) -> bool:
    """
    Verify if string is a valid JSON path.
    """
    return path.startswith("$")
