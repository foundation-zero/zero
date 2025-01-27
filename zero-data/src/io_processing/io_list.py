from dataclasses import dataclass
from enum import Enum

from io_processing.generated_components import Suppliers, Type


class DataType(Enum):
    F32 = "f32"
    BOOL = "bool"
    U32 = "u32"
    I32 = "i32"


def find_type_description(type: str, supplier: Suppliers) -> Type:
    return next(
        (
            type_description
            for type_description in supplier.types
            if type_description.id == type
        ),
    )


def data_type_for_value(value_name: str, type: Type):
    return DataType(type.values[value_name].type.value)


class IoFlavor(Enum):
    AMCS = "amcs"


_DATA_TYPES = {
    IoFlavor.AMCS: {
        "Float": DataType.F32.value,
        "Bool": DataType.BOOL.value,
        "Uint32": DataType.U32.value,
        "Int32": DataType.I32.value,
    }
}


@dataclass
class IOValue:
    data_type: str
    topic: str
