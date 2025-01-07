import re

_camel_case = re.compile(r"(?<!^)(?=[A-Z])")


def snake_case(camel_case: str):
    return _camel_case.sub("_", camel_case).lower()
