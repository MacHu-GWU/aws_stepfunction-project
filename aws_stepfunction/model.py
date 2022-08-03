# -*- coding: utf-8 -*-

import typing as T
import attr


@attr.s
class StepFunctionObject:
    """
    Base class for all serializable StepFunction object.
    """

    def to_dict(
        self,
        exclude_none: bool = True,
        exclude_empty_string: bool = True,
        exclude_empty_collection: bool = True,
    ) -> dict:
        """
        Convert StepFunction Object to Python dict.
        """
        data = dict()
        for k, v in attr.asdict(self).items():
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
    def _re_order(cls, data: dict) -> dict:
        if cls._se_order is None:
            return data
        ordered_data = dict()
        for key in cls._se_order:
            if key in data:
                ordered_data[key] = data[key]
        return ordered_data

    def _pre_serialize_validation(self):
        pass

    def _post_serialize_validation(self, data: dict):
        """
        :param data: the serialization output data.
        """
        pass

    def _serialize(self) -> dict:
        """
        The low level serialization implementation
        """
        raise NotImplementedError

    def serialize(
        self,
        do_pre_validation=True,
        do_post_validation=True,
    ) -> dict:
        if do_pre_validation:
            self._pre_serialize_validation()
        data = self._serialize()
        new_data = self._re_order(data)
        if do_post_validation:
            self._post_serialize_validation(new_data)
        return new_data


StepFunctionObject._se_order: T.Optional[T.List[str]] = None
