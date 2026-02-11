from annotated_types import Gt, Lt

from loads.registry.registry import AT_MODELS, SAIL_SYSTEM_MODELS


def test_no_strict_bounds():
    """Ensure no field use strict gt or lt constraints (use ge or le instead)."""
    fields_with_strict_bounds = [
        f"{model.__name__}.{field}"
        for model in [*AT_MODELS, *SAIL_SYSTEM_MODELS]
        for field, field_info in model.model_fields.items()
        if any(isinstance(m, (Gt, Lt)) for m in field_info.metadata)
    ]

    assert fields_with_strict_bounds == [], (
        f"Fields with strict gt/lt constraints: {fields_with_strict_bounds}"
    )
