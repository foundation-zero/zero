"""
Mock data generator for sail system MQTT topics.

Sail system PLC messages are flat JSON with PLC variable names as keys and
raw integer/boolean values (no MarpowerMessage wrapper).
"""

import random
from typing import Any


from zero_data.data_gen.generator import Generator
from zero_data.io_list.types import IOValue
import logging

logger = logging.getLogger(__name__)


class SailSystemGenerator(Generator):
    def generate_random_value(self, field: IOValue) -> Any:
        if field.data_type.startswith("STRUCT<"):
            return {
                fname: self.generate_random_value(IOValue(fname, ftype))
                for fname, ftype in self._parse_struct_fields(field.data_type)
            }
        match field.data_type:
            case "BOOLEAN":
                return random.choice([True, False])
            case "INTEGER":
                if "position" in field.name.lower():
                    return random.randint(0, 1000)
                return random.randint(0, 2000)
            case "REAL":
                return random.normalvariate(mu=10, sigma=1.0)
        raise KeyError(f"Unknown type: {field.data_type}")

    def _parse_struct_fields(self, struct_type: str) -> list[tuple[str, str]]:
        """Parse STRUCT<name type, ...> into [(name, type)] pairs, handling nesting."""
        inner = struct_type[len("STRUCT<") : -1]
        tokens: list[str] = []
        depth = 0
        buf: list[str] = []
        for ch in inner:
            if ch == "<":
                depth += 1
                buf.append(ch)
            elif ch == ">":
                depth -= 1
                buf.append(ch)
            elif ch == "," and depth == 0:
                tokens.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
        if buf:
            tokens.append("".join(buf).strip())
        return [(t.split(" ", 1)[0], t.split(" ", 1)[1]) for t in tokens if " " in t]
