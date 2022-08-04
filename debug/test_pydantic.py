# -*- coding: utf-8 -*-

import typing as T
from pydantic import BaseModel, fields

class Tag(BaseModel):
    name: str = dataclasses.field()


@dataclasses.dataclass
class Profile:
    ssn: str = dataclasses.field()


@dataclasses.dataclass
class Person:
    id: str = dataclasses.field()
    profile: Profile = dataclasses.field()
    tags: List[Tag] = dataclasses.field(default_factory=list)
