"""I/O types for Modbus bridges."""

from typing import Any, Callable, Literal, get_type_hints

from pydantic import BaseModel, Field, PrivateAttr

RawModbusValue = int | float | bool | None
RegisterValue = tuple[int | None, RawModbusValue]
type TopicConverter[T] = Callable[[list[RegisterValue]], T]


class ModbusField:
    """Describes a single Modbus register or coil.

    Use either `register` (absolute address) or `offset`
    (relative to ``ModbusTopic.start_register``), never both.
    """

    register: int | None = None
    offset: int | None = None
    data_type: Literal["uint16", "float32", "bool"] = "uint16"
    modbus_type: Literal["holding", "coil"] = "holding"
    scale_factor: float = 1.0
    validator: Callable[[RawModbusValue], bool] | None = None

    def __init__(
        self,
        *,
        register: int | None = None,
        offset: int | None = None,
        data_type: Literal["uint16", "float32", "bool"] = "uint16",
        modbus_type: Literal["holding", "coil"] = "holding",
        scale_factor: float = 1.0,
        validator: Callable[[RawModbusValue], bool] | None = None,
    ):
        if register is not None and offset is not None:
            raise ValueError("Provide either `register` or `offset`, not both.")
        self.register = register
        self.offset = offset
        self.data_type = data_type
        self.modbus_type = modbus_type
        self.scale_factor = scale_factor
        self.validator = validator

    @property
    def count(self) -> int:
        """Number of Modbus registers occupied by this field."""
        if self.data_type == "float32":
            return 2
        return 1


class ModbusTopic[T: BaseModel](BaseModel):
    """Describes one MQTT topic backed by Modbus registers.

    Two modes, provided by the two subclasses:

    *Annotation-driven* (``AnnotationModbusTopic``):
        ``model`` carries ``Annotated[..., ModbusField(offset=…)]`` fields.
        The reader introspects annotations, computes absolute register
        addresses from ``start_register``, reads, scales, and serialises.

    *Converter-driven* (``ConverterModbusTopic``):
        ``fields`` lists every register to read.  The reader reads them all
        and passes ``[(abs_register, raw_value), …]`` to ``converter``,
        which returns the JSON payload as a string.
    """

    model_config = {"arbitrary_types_allowed": True}

    topic: str
    model: type[T]
    start_register: int = 0
    unit_id: int = 1
    fields: list[ModbusField] = Field(default_factory=list)
    extra_fields: dict[str, Any] = Field(default_factory=dict)

    _converter: TopicConverter[T] | None = PrivateAttr(default=None)

    @property
    def converter(self) -> TopicConverter[T]:
        """Payload converter; must be provided by subclasses."""
        raise NotImplementedError("converter must be implemented by subclasses")


class AnnotationModbusTopic[T: BaseModel](ModbusTopic[T]):
    """Annotation-driven topic: fields and converter derive from ``model``."""

    def model_post_init(self, __context: Any) -> None:
        annotation_items = list(extract_modbus_fields(self.model).items())

        if annotation_items:
            self.fields = [field for _, field in annotation_items]
            self._converter = build_annotation_converter(
                self.model,
                annotation_items,
                self.extra_fields,
            )

    @property
    def converter(self) -> TopicConverter[T]:
        if self._converter is None:
            raise ValueError(
                f"Model {self.model.__name__} has no annotated ModbusFields"
            )
        return self._converter


class ConverterModbusTopic[T: BaseModel](ModbusTopic[T]):
    """Converter-driven topic: caller provides ``fields`` and ``converter``."""

    def __init__(self, **data: Any) -> None:
        converter = data.pop("converter", None)
        super().__init__(**data)
        if converter is None:
            raise ValueError("ConverterModbusTopic requires fields and converter")
        self._converter = converter

    @property
    def converter(self) -> TopicConverter[T]:
        if self._converter is None:  # unreachable: enforced in __init__
            raise ValueError("ConverterModbusTopic requires fields and converter")
        return self._converter


def _find_modbus_field(hint) -> ModbusField | None:
    if hasattr(hint, "__metadata__"):
        for meta in hint.__metadata__:
            if isinstance(meta, ModbusField):
                return meta
    return None


def extract_modbus_fields(model: type[BaseModel]) -> dict[str, ModbusField]:
    """Extract ``ModbusField`` annotations from a Pydantic model."""
    hints = get_type_hints(model, include_extras=True)
    return {
        name: field
        for name, hint in hints.items()
        if (field := _find_modbus_field(hint)) is not None
    }


def apply_modbus_field(raw: RawModbusValue, field: ModbusField) -> RawModbusValue:
    if raw is None:
        return None
    if field.validator is not None and not field.validator(raw):
        return None
    if isinstance(raw, bool):
        return raw
    return float(raw) * field.scale_factor


def build_annotation_converter[T: BaseModel](
    model: type[T],
    annotation_fields: list[tuple[str, ModbusField]],
    extra_fields: dict[str, Any],
) -> TopicConverter:
    """Create a converter that maps raw register values into model JSON."""

    def converter(values: list[RegisterValue]) -> T:
        field_values: dict[str, RawModbusValue] = {
            name: apply_modbus_field(
                values[idx][1] if idx < len(values) else None, field
            )
            for idx, (name, field) in enumerate(annotation_fields)
        }

        return model(**{**field_values, **extra_fields})

    return converter
