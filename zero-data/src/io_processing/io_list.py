from dataclasses import dataclass
from enum import Enum

from polars import DataFrame, Series
import polars as pl

from io_processing.generated_components import Suppliers, Type


_AMCS_COLS = {
    "Yard Tag": "yard_tag",
    "Tag": "tag",
    "System": "system",
    "Cabinet": "cabinet",
    "Description": "description",
    "Unit": "unit",
    "Deleted": "deleted",
    "Target Type": "type",
}


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


pl_datatypes = pl.Enum(
    [DataType.F32.value, DataType.BOOL.value, DataType.U32.value, DataType.I32.value]
)


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


def normalize_io_list(df: DataFrame, flavor: IoFlavor):
    renamed = df.rename(_AMCS_COLS).filter(pl.col("deleted").is_null())
    typed = renamed.with_columns(
        pl.col("type")
        .replace_strict(_DATA_TYPES[flavor], return_dtype=pl_datatypes)
        .alias("type")
    )
    return typed.with_columns(yard_tag=renamed["yard_tag"].str.replace_all(r"-|_", "-"))
