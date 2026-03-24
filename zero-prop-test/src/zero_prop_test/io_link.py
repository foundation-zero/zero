from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

from aiohttp import ClientSession
from construct import (
    BitStruct,
    Float32b,
    Int16sb,
    Nibble,
    Padding,
    Pointer,
    Struct,
)
from pydantic import BaseModel

from zero_prop_test.settings import Settings


class DeviceStatus(Enum):
    OK = 0
    MAINTENANCE_REQUIRED = 1
    OUT_OF_SPEC = 2
    FUNCTIONAL_CHECK = 3
    FAILURE = 4


class Sm6120(BaseModel):
    """Binary layout for SM6120 process data."""

    quantity: float  # L
    flow: float  # L/min
    temperature: float  # °C
    device_status: DeviceStatus

    # TODO: verify endianness in field
    struct: ClassVar = Struct(
        "quantity" / Pointer(0, Float32b),
        "flow" / Pointer(4, Int16sb),
        "temperature" / Pointer(8, Int16sb),
        "device_status" / Pointer(11, BitStruct(Padding(4), "value" / Nibble)),
    )
    QUANTITY_SCALING: ClassVar = 1000
    FLOW_SCALING: ClassVar = 0.00166667
    FLOW_VALID: ClassVar = range(-25200, 25201)
    TEMPERATURE_SCALING: ClassVar = 0.01
    TEMPERATURE_VALID: ClassVar = range(-4200, 11201)

    @classmethod
    def parse(cls, data: bytes):
        cont = cls.struct.parse(data)
        if cont.flow not in cls.FLOW_VALID:
            raise ValueError(f"Flow value {cont.flow} out of valid range")
        if cont.temperature not in cls.TEMPERATURE_VALID:
            raise ValueError(f"Temperature value {cont.temperature} out of valid range")
        return cls(
            quantity=cont.quantity * cls.QUANTITY_SCALING,
            flow=cont.flow * cls.FLOW_SCALING,
            temperature=cont.temperature * cls.TEMPERATURE_SCALING,
            device_status=DeviceStatus(cont.device_status.value),
        )


class Pn7515(BaseModel):
    pressure: float  # Bar
    device_status: DeviceStatus

    struct: ClassVar = Struct(
        "pressure" / Pointer(0, Int16sb),
        "device_status" / Pointer(3, BitStruct(Padding(4), "value" / Nibble)),
    )
    PRESSURE_VALID: ClassVar = range(-1000, 6301)
    PRESSURE_SCALING: ClassVar = 0.001

    @classmethod
    def parse(cls, data: bytes):
        cont = cls.struct.parse(data)
        if cont.pressure not in cls.PRESSURE_VALID:
            raise ValueError(f"Pressure value {cont.pressure} out of valid range")
        return cls(
            pressure=cont.pressure * cls.PRESSURE_SCALING,
            device_status=DeviceStatus(cont.device_status.value),
        )


type IoLinkDeviceType = Pn7515 | Sm6120


@dataclass
class IoLinkDevice[T]:
    name: str
    yard_tag: str
    address: str
    port: int
    type: type[T]


ADDRESSES = [
    IoLinkDevice("thrusters-flow-fwd", "50001057-22", "192.168.1.2", 1, Sm6120),
    IoLinkDevice("thrusters-flow-aft", "50001057-23", "192.168.1.2", 2, Sm6120),
    IoLinkDevice("thrusters-pressure-relief", "50001097-01", "192.168.1.2", 3, Pn7515),
]


class Client:
    def __init__(
        self,
        session: ClientSession,
        host: str | None = None,
        port: int | None = None,
    ):
        self._session = session
        self._host = host
        self._port = port

    @staticmethod
    def from_settings(settings: Settings) -> "Client":
        return Client(
            session=ClientSession(),
            host=settings.iolink_host,
            port=settings.iolink_port,
        )

    async def query[T: IoLinkDeviceType](self, device: IoLinkDevice[T]) -> T:
        host = self._host if self._host is not None else device.address
        port = f":{self._port}" if self._port is not None else ""
        url = f"http://{host}{port}/iolinkmaster/port[{device.port}]/iolinkdevice/pdin/getdata"
        async with self._session.get(url) as r:
            json_body = await r.json()
            data = json_body["data"]["value"]
            return device.type.parse(bytes.fromhex(data))
