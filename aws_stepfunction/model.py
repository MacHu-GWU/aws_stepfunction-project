# -*- coding: utf-8 -*-

"""
AWS StepFunction data model common module.
"""

import typing as T
import attr
from .constant import Constant as C


class _StepFunctionObject:
    """
    Attributes:

    - ``_field_order``: a private class attribute to provide
        field order information for serialization.
    """
    _field_order: T.List[str] = None


@attr.s
class StepFunctionObject(_StepFunctionObject):
    """
    Base class for all serializable StepFunction object.
    """

    def to_dict(
        self,
        exclude_none: bool = True,
        exclude_empty_string: bool = True,
        exclude_empty_collection: bool = True,
        exclude_private_attr: bool = True
    ) -> dict:
        """
        Convert StepFunction Object to Python dict.

        A revision of the ``attr.asdict`` API, allow to exclude:

        - None
        - empty string
        - empty collection (list, dict)
        """
        data = dict()
        for k, v in attr.asdict(self).items():
            if k.startswith("_"):
                if exclude_private_attr:
                    continue

            if v is None:
                if exclude_none:
                    continue
            elif isinstance(v, str):
                if len(v) == 0:
                    if exclude_empty_string:
                        continue
            elif isinstance(v, (list, dict)):
                if len(v) == 0:
                    if exclude_empty_collection:
                        continue
            else:
                pass
            data[k] = v
        return data

    @classmethod
    def _to_alias(cls, data: dict) -> dict:
        """
        Change Python class attribute name to StepFunction JSON field name
        (if available). Alias information is stored in class field definition
        metadata.

        For example, ``Workflow._start_at`` -> ``StartAt``.
        """
        mapper = {
            field.name: field.metadata.get(C.ALIAS, field.name)
            for field in attr.fields(cls)
        }
        return {
            mapper.get(k, k): v
            for k, v in data.items()
        }

    @classmethod
    def _sort_field(cls, data: dict) -> dict:
        """
        Sort the field based on the defined ``_field_order`` class attribute.
        """
        if cls._field_order is None:
            return data
        ordered_data = dict()
        for key in cls._field_order:
            if key in data:
                ordered_data[key] = data[key]
        return ordered_data

    def _pre_serialize_validation(self): # pragma: no cover
        """
        A pre-serialization hook for validation.
        """
        pass

    def _post_serialize_validation(self, data: dict): # pragma: no cover
        """
        A post-serialization hook for validation.

        :param data: the serialization output data.
        """
        pass

    def _serialize(self) -> dict: # pragma: no cover
        """
        The low level serialization implementation.
        """
        raise NotImplementedError

    def serialize(
        self,
        do_pre_validation=True,
        do_post_validation=True,
    ) -> dict:
        """
        Public API for serialization
        """
        if do_pre_validation:
            self._pre_serialize_validation()
        data = self._serialize()
        # DO NOT call self._to_alias here, let the subclass decides
        # when should call it
        new_data = self._sort_field(data)
        if do_post_validation:
            self._post_serialize_validation(new_data)
        return new_data
