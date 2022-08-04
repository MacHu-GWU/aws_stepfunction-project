# -*- coding: utf-8 -*-

import attr

from .exc import ValidationError
from .model import StepFunctionObject


@attr.s
class _IsInstanceValidator:
    type = attr.ib()

    def __call__(
        self,
        inst: StepFunctionObject,
        attr: str,
        value,
    ):
        if not isinstance(value, self.type):
            raise ValidationError(
                f"'{attr}' must be {self.type!r} "
                f"(got {value!r} that is a {value.__class__!r})."
            )
