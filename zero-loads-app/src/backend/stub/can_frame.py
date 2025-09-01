from construct import (
    Struct,
    BitStruct,
    Bitwise,
    BitsInteger,
    Flag,
    FlagsEnum,
    Int8ub,
    Int16ub,
    Int32ub,
    Int32ul,
    Bytes,
    Computed,
    Const,
    this,
)


# -------------------------
# Shared building blocks
# -------------------------

# 32-bit CAN ID field — classic CAN (has RTR bit)
CANID_Classical = BitStruct(
    "id" / BitsInteger(29),  # bits 0..28
    "reserved0" / BitsInteger(1),  # bit 29, fixed 0
    "rtr" / Flag,  # bit 30
    "extended" / Flag,  # bit 31 (1 = extended frame)
)

# 32-bit CAN ID field — CAN FD (no RTR bit; bits 29..30 fixed 0)
CANID_FD = Bitwise(
    BitStruct(
        "id" / BitsInteger(29),  # bits 0..28
        "reserved0" / BitsInteger(1),  # bits 29, fixed 0
        "rtr" / BitsInteger(1),  # bit 30 (rtr)
        "extended" / Flag,  # bit 31 (1 = extended frame)
    )
)

# Flags fields
ClassicalFlags = FlagsEnum(
    Int16ub,
    RTR=0x0001,  # Remote Transmission Request
    EXTENDED=0x0002,  # Extended ID
)

FDFlags = FlagsEnum(
    Int16ub,
    EXTENDED=0x0002,  # Extended ID
    EDL=0x0010,  # Extended Data Length
    BRS=0x0020,  # Bit Rate Switch
    ESI=0x0040,  # Error State Indicator
)


# -------------------------
# Frame definitions
# -------------------------

# 1) Classic CAN 2.0 A/B (Message Type = 0x80)
ClassicCAN_IPFrame = Struct(
    "length" / Int16ub,  # total packet length incl. this field
    "message_type" / Const(0x80, Int16ub),  # 0x80
    "tag" / Bytes(8),  # not used currently
    "ts_low" / Int32ub,  # timestamp (µs), low 32
    "ts_high" / Int32ub,  # timestamp (µs), high 32
    "channel" / Int8ub,  # not used (route defines channel)
    "dlc" / Int8ub,  # number of valid data bytes (0..8)
    "flags" / ClassicalFlags,  # RTR / EXTENDED
    "can_id" / CANID_Classical,
    # Spec says this field ALWAYS carries 8 bytes; bytes after DLC are invalid
    "data" / Bytes(8),
    # Convcenience: computed CAN identifier (11 or 29 bits)
    "can_identifier"
    / Computed(
        lambda ctx: ctx.can_id.id if ctx.can_id.extended else ctx.can_id.id & 0x7FF
    ),
    # Convenience: slice valid payload
    "payload" / Computed(lambda ctx: ctx.data[: ctx.dlc]),
)

# 2) Classic CAN 2.0 A/B WITH CRC32 (Message Type = 0x81)
ClassicCAN_CRC_IPFrame = Struct(
    "length" / Int16ub,
    "message_type" / Const(0x81, Int16ub),  # 0x81
    "tag" / Bytes(8),
    "ts_low" / Int32ub,
    "ts_high" / Int32ub,
    "channel" / Int8ub,
    "dlc" / Int8ub,
    "flags" / ClassicalFlags,
    "can_id" / CANID_Classical,
    "data" / Bytes(8),
    "can_identifier"
    / Computed(
        lambda ctx: ctx.can_id.id if ctx.can_id.extended else ctx.can_id.id & 0x7FF
    ),
    "payload" / Computed(lambda ctx: ctx.data[: ctx.dlc]),
    # CRC32 is appended LITTLE-endian according to the spec
    "crc32" / Int32ul,
)

# 3) CAN FD (Message Type = 0x90)
CANFD_IPFrame = Struct(
    "length" / Int16ub,
    "message_type" / Const(0x90, Int16ub),  # 0x90
    "tag" / Bytes(8),
    "ts_low" / Int32ub,
    "ts_high" / Int32ub,
    "channel" / Int8ub,
    "dlc" / Int8ub,
    "flags" / FDFlags,  # EXTENDED, EDL, BRS, ESI
    "can_id" / CANID_FD,
    # For FD, only as many bytes as necessary are transmitted
    "data" / Bytes(this.dlc),
    "can_identifier"
    / Computed(
        lambda ctx: ctx.can_id.id if ctx.can_id.extended else ctx.can_id.id & 0x7FF
    ),
    "payload" / Computed(lambda ctx: ctx.data),
)

# 4) CAN FD WITH CRC32 (Message Type = 0x91)
CANFD_CRC_IPFrame = Struct(
    "length" / Int16ub,
    "message_type" / Const(0x91, Int16ub),  # 0x91
    "tag" / Bytes(8),
    "ts_low" / Int32ub,
    "ts_high" / Int32ub,
    "channel" / Int8ub,
    "dlc" / Int8ub,
    "flags" / FDFlags,
    "can_id" / CANID_FD,
    "data" / Bytes(this.dlc),
    "can_identifier"
    / Computed(
        lambda ctx: ctx.can_id.id if ctx.can_id.extended else ctx.can_id.id & 0x7FF
    ),
    "payload" / Computed(lambda ctx: ctx.data),
    "crc32" / Int32ul,
)
