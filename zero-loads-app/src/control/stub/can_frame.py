from construct import (
    Struct,
    BitStruct,
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

# 32-bit CAN ID field
CAN_ID = BitStruct(
    "id" / BitsInteger(29),  # bits 0..28
    "reserved0" / BitsInteger(1),  # bit 29, fixed 0
    "rtr" / Flag,  # Remote Transmission Request, bit 30
    "extended" / Flag,  # Extended ID, bit 31
)

# Flags fields
CLASSIC_FLAGS = FlagsEnum(
    Int16ub,
    rtr=0x01,  # Remote Transmission Request
    extended=0x02,  # Extended ID
)

FD_FLAGS = FlagsEnum(
    Int16ub,
    extended=0x02,  # Extended ID
    edl=0x10,  # Extended Data Length
    brs=0x20,  # Bit Rate Switch
    esi=0x40,  # Error State Indicator
)


# -------------------------
# Frame definitions
# -------------------------

# 1) Classic CAN 2.0 A/B (Message Type = 0x80)
CAN_Frame = Struct(
    "length" / Int16ub,  # total packet length incl. this field
    "message_type" / Const(0x80, Int16ub),  # 0x80
    "tag" / Bytes(8),  # not used currently
    "ts_low" / Int32ub,  # timestamp (µs), low 32
    "ts_high" / Int32ub,  # timestamp (µs), high 32
    "channel" / Int8ub,  # not used (route defines channel)
    "dlc" / Int8ub,  # number of valid data bytes (0..8)
    "flags" / CLASSIC_FLAGS,  # RTR / EXTENDED
    "can_id" / CAN_ID,
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
CAN_CRC_Frame = Struct(
    "length" / Int16ub,
    "message_type" / Const(0x81, Int16ub),  # 0x81
    "tag" / Bytes(8),
    "ts_low" / Int32ub,
    "ts_high" / Int32ub,
    "channel" / Int8ub,
    "dlc" / Int8ub,
    "flags" / CLASSIC_FLAGS,
    "can_id" / CAN_ID,
    "data" / Bytes(8),
    "can_identifier"
    / Computed(
        lambda ctx: ctx.can_id.id if ctx.can_id.extended else ctx.can_id.id & 0x7FF
    ),
    "payload" / Computed(lambda ctx: ctx.data[: ctx.dlc]),
    "crc32" / Int32ul,  # CRC32 is appended little-endian
)

# 3) CAN FD (Message Type = 0x90)
CAN_FD_Frame = Struct(
    "length" / Int16ub,
    "message_type" / Const(0x90, Int16ub),  # 0x90
    "tag" / Bytes(8),
    "ts_low" / Int32ub,
    "ts_high" / Int32ub,
    "channel" / Int8ub,
    "dlc" / Int8ub,
    "flags" / FD_FLAGS,  # EXTENDED, EDL, BRS, ESI
    "can_id" / CAN_ID,
    # For FD, only as many bytes as necessary are transmitted
    "data" / Bytes(this.dlc),
    "can_identifier"
    / Computed(
        lambda ctx: ctx.can_id.id if ctx.can_id.extended else ctx.can_id.id & 0x7FF
    ),
    "payload" / Computed(lambda ctx: ctx.data),
)

# 4) CAN FD WITH CRC32 (Message Type = 0x91)
CAN_FD_CRC_Frame = Struct(
    "length" / Int16ub,
    "message_type" / Const(0x91, Int16ub),  # 0x91
    "tag" / Bytes(8),
    "ts_low" / Int32ub,
    "ts_high" / Int32ub,
    "channel" / Int8ub,
    "dlc" / Int8ub,
    "flags" / FD_FLAGS,
    "can_id" / CAN_ID,
    "data" / Bytes(this.dlc),
    "can_identifier"
    / Computed(
        lambda ctx: ctx.can_id.id if ctx.can_id.extended else ctx.can_id.id & 0x7FF
    ),
    "payload" / Computed(lambda ctx: ctx.data),
    "crc32" / Int32ul,
)
