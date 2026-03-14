from asyncio import TaskGroup
import asyncio
from concurrent.futures import Executor, ThreadPoolExecutor, Future
from datetime import datetime
from enum import Enum
import logging
from threading import Lock
import traceback
from typing import Generator, Iterator, cast
from dataclasses import dataclass
from typing import AsyncIterator

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractIncomingMessage
from iceburger.settings import Config, Settings, RoutingConfig

from pyiceberg.catalog import load_catalog, Catalog
import polars as pl
from pyiceberg.schema import Schema

logger = logging.getLogger(__name__)


class Receiver:
    def __init__(
        self,
        connection: AbstractRobustConnection,
        exchange_name: str,
        queue_name: str,
        routing_keys: list[str],
    ):
        self._connection = connection
        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self._routing_keys = routing_keys

    @staticmethod
    async def from_settings(settings: Settings, config: Config) -> "Receiver":
        connection = await aio_pika.connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_username,
            password=settings.rabbitmq_password,
        )
        return Receiver(
            connection,
            config.amqp.exchange,
            config.amqp.queue,
            config.amqp.routing_keys,
        )

    async def receive(self):
        channel = await self._connection.channel()
        queue = await channel.declare_queue(
            self._queue_name, durable=True
        )  # Ensure the queue exists
        for key in self._routing_keys:
            await queue.bind(exchange=self._exchange_name, routing_key=key)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logger.info(
                    f"Received message with body: {message.body} on routing key: {message.routing_key} at timestamp: {message.timestamp}"
                )
                yield message


class QueueStatus(Enum):
    OK = 1
    FULL = 2


class Queue[I, T]:
    """A thread-safe queue

    This queue preallocated a given capacity and will signal when it is full.
    When full it can still take in new messages, but the caller should swap the queue soonish (ideally before the capacity is reached).
    """

    # TODO: it might be interesting to specialise a queue to pre-batch messages into DataFrames and then diagonally stack those. That would reduce memory usage.

    def __init__(self, size: int, capacity: int, empty: I):
        self._messages: list[I] = [empty] * capacity
        self._empty = empty
        self._size = size
        self._capacity = capacity
        self._index = 0
        self._lock = Lock()
        self._track: T | None = None

    def swap_tracked(self) -> tuple[list[I], T | None]:
        with self._lock:
            new: list[I] = [self._empty] * self._capacity
            messages, self._messages = self._messages, new
            track, self._track = self._track, None
            self._index = 0
            return cast(list[I], messages), track

    def swap(self) -> list[I]:
        return self.swap_tracked()[0]

    def insert(self, message: I, track=None) -> QueueStatus:
        with self._lock:
            self._track = track
            if self._index >= self._capacity:
                self._messages.append(message)
            else:
                self._messages[self._index] = message
            self._index += 1
            if self._index >= self._size:
                return QueueStatus.FULL
            else:
                return QueueStatus.OK


type Msg = tuple[bytes, str, datetime, int] | tuple[None, None, None, None]


@dataclass
class TableConfig:
    name: str
    timestamp: bool
    include_routing_key: bool

    @staticmethod
    def from_topic_settings(
        topic_settings: RoutingConfig, namespace: str
    ) -> "TableConfig":
        return TableConfig(
            name=f"{namespace}.{topic_settings.table}",
            timestamp=topic_settings.timestamp,
            include_routing_key=not topic_settings.exclude_routing_key,
        )


type FanoutResult = tuple[Queue[Msg, AbstractIncomingMessage], TableConfig]


class Fanout:
    def __init__(
        self,
        topic_settings: list[RoutingConfig],
        batch_size: int,
        iceberg_namespace: str,
    ):
        self._queues = {
            topic_setting.table: (
                Queue[Msg, AbstractIncomingMessage](
                    size=batch_size,
                    capacity=batch_size * 2,
                    empty=(None, None, None, None),
                ),
                TableConfig.from_topic_settings(
                    topic_setting, namespace=iceberg_namespace
                ),
            )
            for topic_setting in topic_settings
        }
        self._topic_settings = topic_settings
        self._batch_size = batch_size
        self._full_queues = set()

    @staticmethod
    def from_settings(settings: Settings, config: Config) -> "Fanout":
        return Fanout(config.routings, config.batch.size, settings.iceberg_namespace)

    async def process(self, messages: AsyncIterator[AbstractIncomingMessage]):
        async for message in messages:
            if message.routing_key is None:
                logger.info(
                    f"Received message without routing key, skipping: {message.body}"
                )
                continue
            queue, table = self.ensure_queue(message.routing_key)

            status = queue.insert(
                (
                    message.body,
                    message.routing_key,
                    cast(datetime, message.timestamp),
                    cast(int, message.delivery_tag),
                ),
                track=message,
            )
            if status == QueueStatus.FULL:
                logger.info(f"Queue for table {table.name} is full")
                self._full_queues.add(table.name)

    @property
    def queues(
        self,
    ) -> dict[str, FanoutResult]:
        return self._queues

    def full_queues(
        self,
    ) -> Generator[
        FanoutResult,
        None,
        None,
    ]:
        for table in self._full_queues:
            yield self._queues[table]

    def clear_full_queues(self):
        self._full_queues.clear()

    def ensure_queue(
        self, routing_key: str
    ) -> tuple[Queue[Msg, AbstractIncomingMessage], TableConfig]:
        for topic_setting in self._topic_settings:
            if routing_key.startswith(topic_setting.routing_key_prefix):
                return self._queues[topic_setting.table]

        table_name = routing_key.replace("/", "_")
        self._queues[table_name] = (
            Queue[Msg, AbstractIncomingMessage](
                size=self._batch_size,
                capacity=self._batch_size * 2,
                empty=(None, None, None, None),
            ),
            TableConfig(name=table_name, timestamp=True, include_routing_key=False),
        )
        return self._queues[table_name]


@dataclass
class Table:
    config: TableConfig
    items: list[Msg]
    ack: AbstractIncomingMessage | None = None


class Sweeper:
    def __init__(self, interval: int):
        self._interval = interval
        self._iterator = None

    @staticmethod
    async def from_settings(config: Config) -> "Sweeper":
        return Sweeper(config.batch.seconds)

    def tick(self, fanout: Fanout) -> Iterator[Table]:
        for queue, config in fanout.full_queues():
            items, msg = queue.swap_tracked()
            yield Table(config=config, items=items, ack=msg)
        fanout.clear_full_queues()

        if self._iterator is None:
            self._iterator = iter(fanout.queues.copy().values())

        try:
            queue, config = next(self._iterator)
            items, msg = queue.swap_tracked()
            if items and items[0][0] is not None:
                yield Table(config=config, items=items, ack=msg)
        except StopIteration:
            self._iterator = None

    async def sweep(self, fanout: Fanout) -> AsyncIterator[Table]:
        while True:
            async with TaskGroup() as tg:
                tg.create_task(asyncio.sleep(self._interval / len(fanout.queues)))
                for table in self.tick(fanout):
                    yield table


class Sink:
    def __init__(self, catalog: Catalog, loop: asyncio.AbstractEventLoop):
        self._catalog = catalog
        self._loop = loop

    @staticmethod
    async def from_settings(settings: Settings) -> "Sink":
        logger.info(f"Loading Iceberg catalog with {settings}")
        catalog = load_catalog(
            name=settings.iceberg_catalog_type,
            uri=settings.iceberg_catalog_uri,
            warehouse=settings.iceberg_warehouse,
            **{
                "s3.endpoint": settings.s3_endpoint,
                "s3.access-key-id": settings.s3_access_key_id,
                "s3.secret-access-key": settings.s3_secret_access_key,
                "s3.region": settings.s3_region,
            },
        )
        return Sink(catalog, asyncio.get_event_loop())

    def _cols(self, config: TableConfig) -> list[str]:
        cols = []
        if config.include_routing_key:
            cols.append("routing_key")
        if config.timestamp:
            cols.append("timestamp")
        return cols

    def convert_schema(self, original: Schema, df_schema) -> Schema:
        converted = self._catalog._convert_schema_if_needed(df_schema)
        fields = [
            field.model_copy(update={"field_id": original_field.field_id})
            for field in converted.fields
            if (original_field := original.find_field(field.name))
        ]
        return converted.model_copy(update={"fields": fields})

    def write(self, table: Table):
        input_df = (
            pl.from_records(
                table.items,
                {
                    "msg": pl.Binary,
                    "routing_key": pl.Utf8,
                    "timestamp": pl.Datetime,
                    "delivery_tag": pl.Int64,
                },
                orient="row",
                strict=False,
            )
            .drop("delivery_tag")
            .drop_nulls(subset=["msg"])
        )

        if input_df.is_empty():
            logger.info("Skipping empty batch")
            return
        else:
            logger.info(f"Writing batch of {len(table.items)} messages")

        decoded = pl.DataFrame(
            input_df.get_column("msg").cast(pl.Utf8).str.json_decode()
        ).unnest("msg")

        df = decoded.hstack(input_df.select(self._cols(table.config))).to_arrow()

        logger.info("Ensuring table")
        iceberg_table = self._catalog.create_table_if_not_exists(
            table.config.name, schema=df.schema
        )
        logger.info(f"Appending {len(df)} rows to table")
        converted_schema = self.convert_schema(iceberg_table.schema(), df.schema)
        try:
            if iceberg_table.schema() != converted_schema:
                logger.info(
                    f"Evolving schema from {iceberg_table.schema()} to {converted_schema}"
                )
                with iceberg_table.update_schema() as update_schema:
                    update_schema.union_by_name(df.schema)
                logger.info("Finished evolving schema, appending data")

            iceberg_table.append(df)
            logger.info(
                f"Wrote batch of {len(table.items)} messages to Iceberg table {table.config.name}"
            )
        except ValueError as e:
            logger.error(
                f"{e} Unable to evolve schema for table {table.config.name}. Table schema: {iceberg_table.schema()}, DataFrame schema: {df.schema}"
            )
            # TODO: handle this better. Options:
            # Have table of raw json as a last effort dump
            # Increment table version (but this drops parallism, because both workers would create a new table)

        if table.ack:

            async def _do_acks(msg: AbstractIncomingMessage):
                for _, _, _, delivery_tag in table.items:
                    if delivery_tag is None:
                        break
                    await msg.channel.basic_ack(delivery_tag)

            self._loop.create_task(_do_acks(table.ack))


class Iceburger:
    def __init__(
        self,
        receiver: Receiver,
        fanout: Fanout,
        sweeper: Sweeper,
        sink: Sink,
        executor: Executor,
    ):
        self._receiver = receiver
        self._fanout = fanout
        self._sweeper = sweeper
        self._executor = executor
        self._sink = sink

    @staticmethod
    async def from_settings(settings: Settings, config: Config) -> "Iceburger":
        receiver = await Receiver.from_settings(settings, config)
        fanout = Fanout.from_settings(settings, config)
        sweeper = await Sweeper.from_settings(config)
        sink = await Sink.from_settings(settings)
        executor = ThreadPoolExecutor(max_workers=settings.sink_workers)
        return Iceburger(receiver, fanout, sweeper, sink, executor)

    def _finish(self, fut: Future[None]):
        if fut.exception():
            logger.error(f"Error writing batch: {fut.exception()}")
            logger.error("\n".join(traceback.format_exception(fut.exception())))
        else:
            logger.info("Finished writing batch")

    async def _process_sweeping(self):
        async for table in self._sweeper.sweep(self._fanout):
            result = self._executor.submit(self._sink.write, table)
            result.add_done_callback(self._finish)

    async def run(self):
        messages = self._receiver.receive()
        async with TaskGroup() as tg:
            tg.create_task(self._fanout.process(messages))
            tg.create_task(self._process_sweeping())
