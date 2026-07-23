"""I/O types for Modbus bridges."""

from typing import Any, Callable, Literal, get_type_hints

from pydantic import BaseModel, Field

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
    count: int = 1
    data_type: Literal["uint16", "float32", "bool"] = "uint16"
    modbus_type: Literal["holding", "coil"] = "holding"
    scale_factor: float = 1.0
    invalid_value: int | None = None

    def __init__(
        self,
        *,
        register: int | None = None,
        offset: int | None = None,
        count: int = 1,
        data_type: Literal["uint16", "float32", "bool"] = "uint16",
        modbus_type: Literal["holding", "coil"] = "holding",
        scale_factor: float = 1.0,
        invalid_value: int | None = None,
    ):
        if register is not None and offset is not None:
            raise ValueError("Provide either `register` or `offset`, not both.")
        self.register = register
        self.offset = offset
        self.count = count
        self.data_type = data_type
        self.modbus_type = modbus_type
        self.scale_factor = scale_factor
        self.invalid_value = invalid_value


class ModbusTopic[T: BaseModel](BaseModel):
    """Describes one MQTT topic backed by Modbus registers.

    Two modes:

    *Annotation-driven* (``converter=None``):
        ``model`` carries ``Annotated[..., ModbusField(offset=…)]`` fields.
        The reader introspects annotations, computes absolute register
        addresses from ``start_register``, reads, scales, and serialises.

    *Converter-driven* (``converter`` set):
        ``fields`` lists every register to read.  The reader reads them all
        and passes ``[(abs_register, raw_value), …]`` to ``converter``,
        which returns the JSON payload as a string.
    """

    model_config = {"arbitrary_types_allowed": True}

    topic: str
    model: type[T]
    start_register: int = 0
    unit_id: int = 1
    fields: list[ModbusField] | None = None
    extra_fields: dict[str, Any] = Field(default_factory=dict)
    converter: TopicConverter[T] | None = None

    def model_post_init(self, __context: Any) -> None:
        annotations = extract_modbus_fields(self.model)
        annotation_items = list(annotations.items())

        if self.fields is None and annotation_items:
            self.fields = [field for _, field in annotation_items]

        if self.converter is None and annotation_items:
            self.converter = build_annotation_converter(
                self.model,
                annotation_items,
                self.extra_fields,
            )


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
    if field.invalid_value is not None and raw == field.invalid_value:
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
