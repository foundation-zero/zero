from typing import cast

from input_output.base import ThrsModel


class ModelBuilder[T: ThrsModel]:
    def __init__(self, cls: type[T]):
        self._cls = cls
        self._init_data = {}
        self._model: T | None = None

    def input(self, key: str, message: str):
        parsed_message = cast(
            ThrsModel, self._cls.model_fields[key].annotation
        ).model_validate_json(message)
        if self._model is None:
            self._init_data[key] = parsed_message
            if (
                self._cls.model_fields.keys() == self._init_data.keys()
            ):  # all keys present
                self._model = self._cls.model_construct(**self._init_data)  # type: ignore
        else:
            setattr(self._model, key, parsed_message)

    def result(self) -> T | None:
        return self._model
