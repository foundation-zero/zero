import re


def hyphenize(text: str):
    return text.replace("_", "-")


uppercase_regex = re.compile(r"([A-Z])")


def camel_to_kebab(text: str) -> str:
    return uppercase_regex.sub(r"-\1", text).lower().removeprefix("-")


def camel_to_title(text: str) -> str:
    return uppercase_regex.sub(r" \1", text).title().strip()


def snake_to_title(text: str) -> str:
    return text.replace("_", " ").title()


def ensure_list[T](x: T | list[T]) -> list[T]:
    """Provide list or single object, return list in both cases"""
    return x if isinstance(x, list) else [x]
