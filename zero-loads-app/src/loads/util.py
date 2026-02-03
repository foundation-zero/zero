import re


def hyphenize(text: str):
    return text.replace("_", "-")


uppercase_regex = re.compile(r"([A-Z])")


def camel_to_kebab(text: str) -> str:
    return uppercase_regex.sub(r"-\1", text).lower().removeprefix("-")
