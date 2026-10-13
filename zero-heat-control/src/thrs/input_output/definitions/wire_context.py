from enum import StrEnum


class WireContext(StrEnum):
    """Context in which values are communicated over the wire.

    - `ACTUATED`: what the AMCS actually did (`CC_` prefixed keys); also used
      by the simulation, which mimics the AMCS.
    - `COMMANDED`: commands sent to the AMCS (plain keys).

    (no context): used for internal communication (e.g. manual values from the API to the control)
    """

    ACTUATED = "actuated"
    COMMANDED = "commanded"


AMCS_RECEIVE_CONTEXT = WireContext.ACTUATED
AMCS_WRITE_CONTEXT = WireContext.COMMANDED


def is_actuated(context: object) -> bool:
    return context is WireContext.ACTUATED


def is_commanded(context: object) -> bool:
    return context is WireContext.COMMANDED
