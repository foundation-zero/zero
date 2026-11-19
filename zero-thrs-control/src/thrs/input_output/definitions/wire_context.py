from enum import StrEnum


class WireContext(StrEnum):
    """Context in which values are communicated over the wire.

    - `ACTUATED`: what the AMCS actually did (`CC_` prefixed keys); also used
      by the simulation, which mimics the AMCS.
    - `COMMANDED`: commands sent to the AMCS (plain keys).
    - `SET`: a client's write on a `/set` topic. A stamped value may leave out
      its `TimeStamp`; it is then stamped when it arrives.

    (no context): used for internal communication
    """

    ACTUATED = "actuated"
    COMMANDED = "commanded"
    SET = "set"


AMCS_RECEIVE_CONTEXT = WireContext.ACTUATED
AMCS_WRITE_CONTEXT = WireContext.COMMANDED


def is_actuated(context: object) -> bool:
    return context is WireContext.ACTUATED


def is_commanded(context: object) -> bool:
    return context is WireContext.COMMANDED


def is_set(context: object) -> bool:
    return context is WireContext.SET
