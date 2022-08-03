# -*- coding: utf-8 -*-

import uuid
import hashlib


def short_uuid(n: str = 7) -> str:
    """
    return short uuid.
    """
    m = hashlib.sha1()
    m.update(uuid.uuid4().bytes)
    return m.hexdigest()[:n]
