from typing import Any, Literal


def get_model_from_to_diff(
    model_from: dict[str, Any], model_to: dict[str, Any]
) -> dict[str, dict[Literal["from", "to"], Any]]:
    """Get the difference between the from and to model. Output is a dict of the form {key: {"from": value_from, "to": value_to}} for each key that has a different value in the from and to model."""
    return {
        key: {"from": model_from[key], "to": model_to[key]}
        for key in model_from.keys()
        if model_from[key] != model_to[key]
    }
