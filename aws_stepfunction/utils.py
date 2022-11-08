# -*- coding: utf-8 -*-

"""
Utility functions.
"""

import typing as T
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


DELIMITERS = ["_", "-", " "]


def tokenize(s: str) -> T.List[str]:
    """
    Tokenize the text into words.
    """
    for sep in DELIMITERS:
        s = s.replace(sep, " ")
    return [token for token in s.split(" ") if token]


def slugify(s: str) -> str:
    """
    Convert to lowercase + hyphen naming convention.
    """
    return "-".join([token.lower() for token in tokenize(s)])


def snake_case(s: str) -> str:
    """
    Convert to lowercase + underscore naming convention.
    """
    return "_".join([token.lower() for token in tokenize(s)])


def camel_case(s: str) -> str:
    """
    Convert to first letter uppercase + no space naming convention.
    """
    return "".join([token[0].upper() + token[1:].lower() for token in tokenize(s)])
