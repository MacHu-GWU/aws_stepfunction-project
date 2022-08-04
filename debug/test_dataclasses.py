# -*- coding: utf-8 -*-

import dataclasses
from typing import List


@dataclasses.dataclass
class Base:
    id: str = dataclasses.field()


@dataclasses.dataclass
class Item(Base):
    name: str = dataclasses.field()


@dataclasses.dataclass
class Apple(Item):
    color: str = dataclasses.field()


Item(id="id-1", name="apple")
Apple(id="id-2", name="apple", color="red")


@dataclasses.dataclass
class Tag:
    id: int = dataclasses.field()
    name: str = dataclasses.field()


@dataclasses.dataclass
class Profile:
    ssn: str = dataclasses.field()


@dataclasses.dataclass
class Person:
    id: str = dataclasses.field()
    profile: Profile = dataclasses.field()
    tags: List[Tag] = dataclasses.field(default_factory=list)


person = Person(
    id="p1",
    profile=Profile(ssn="123-456-7890"),
    tags=[
        Tag(id=1, name="tag1"), Tag(id=2, name="tag2")
    ]
)

person_data = dataclasses.asdict(person)
print(person_data)
person = Person(**person_data)
print(person.profile)
