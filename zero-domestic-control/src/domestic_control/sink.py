from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager
from typing import AsyncIterator, Protocol

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from domestic_control.messages import (
    Amplifier,
    Blind,
    LightingGroup,
    Message,
    Model,
)

type PersistedMessage = Amplifier | Blind | LightingGroup
type SinkMessage = Message | Model


class Sink(Protocol):
    async def send(self, message: SinkMessage): ...


class BeginSink(Protocol):
    def send_begin(self, message: SinkMessage) -> AbstractAsyncContextManager[None]: ...


class CompositeSink:
    """Fan-out sink.

    This sink allows sending messages to multiple sinks, with support for transactional sinks that require a begin context. The begin sinks are entered before any messages are sent, ensuring that all sinks operate within the same transaction if needed.
    """

    def __init__(self, begin_sinks: list[BeginSink], sinks: list[Sink]):
        self._begin_sinks = begin_sinks
        self._sinks = sinks

    async def send(self, message: SinkMessage):
        async with AsyncExitStack() as stack:
            for begin_sink in self._begin_sinks:
                await stack.enter_async_context(begin_sink.send_begin(message))

            for sink in self._sinks:
                await sink.send(message)


class PostgresSink(BeginSink):
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    @asynccontextmanager
    async def send_begin(self, message: SinkMessage) -> AsyncIterator[None]:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                data = message.model_dump()
                if data.keys() == {"id"}:
                    return
                stmt = (
                    insert(type(message))
                    .values(data)
                    .on_conflict_do_update(
                        index_elements=["id"],
                        set_={key: value for key, value in data.items() if key != "id"},
                    )
                )
                await session.exec(stmt)
                yield

    async def send(self, message: SinkMessage):
        async with self.send_begin(message):
            pass
