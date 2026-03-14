import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from random import random
from time import sleep
from typing import AsyncIterator, cast
from typing import Iterable
from unittest.mock import MagicMock
from aio_pika import IncomingMessage
from iceburger.iceburger import (
    Fanout,
    Queue,
    QueueStatus,
    Sink,
    Sweeper,
    Table,
    TableConfig,
)
from iceburger.settings import RoutingConfig
import pytest
from pyiceberg.catalog import Catalog
from pyiceberg.table import Table as IcebergTable
import polars as pl


class TestQueue:
    def test_queue(self):
        queue = Queue[None | int, None](size=10, capacity=20, empty=None)
        for i in range(9):
            assert queue.insert(i) == QueueStatus.OK
        assert queue.insert(9) == QueueStatus.FULL
        assert queue.swap() == (list(range(10)) + ([None] * 10))

    def test_thread_safety(self):
        queue = Queue[None | int, None](size=10, capacity=20, empty=None)

        def _do(start):
            for i in range(start, start + 10):
                sleep(random() * 0.01)
                queue.insert(i)
            return queue.swap()

        with ThreadPoolExecutor(max_workers=100) as executor:
            results = list(executor.map(_do, range(0, 1000, int(1000 / 100))))
            end_result = [
                num for result in results for num in result if num is not None
            ]

        assert len(end_result) == 100 * 10
        assert set(end_result) == set(range(0, 1000))


async def async_iter[T](iter: Iterable[T]) -> AsyncIterator[T]:
    for item in iter:
        yield item


def compact[T](a: list[T]) -> list[T]:
    return [x for x in a if x is not None]


def compact_tuple[T: tuple](a: list[T]) -> list[T]:
    return [x for x in a if x[0] is not None]


class TestFanout:
    async def test_fanout(self):
        topic_settings = [
            RoutingConfig(routing_key_prefix="a", table="table_a", timestamp=False),
            RoutingConfig(routing_key_prefix="b", table="table_b", timestamp=False),
        ]
        fanout = Fanout(
            topic_settings=topic_settings, batch_size=10, iceberg_namespace="default"
        )

        id = [0]

        class Message:
            def __init__(self, routing_key: str, body: bytes):
                self.routing_key = routing_key
                self.body = body
                self.timestamp = datetime.now()
                id[0] += 1
                self.delivery_tag = id[0]

        messages = cast(
            list[IncomingMessage],
            [
                Message(routing_key="a/1", body=b"{}"),
                Message(routing_key="a/2", body=b"{}"),
                Message(routing_key="b/1", body=b"{}"),
                Message(routing_key="not-collated/1", body=b"{}"),
            ],
        )
        await fanout.process(async_iter(messages))

        assert len(compact_tuple(fanout.queues["table_a"][0].swap())) == 2
        assert len(compact_tuple(fanout.queues["table_b"][0].swap())) == 1
        assert len(compact_tuple(fanout.queues["not-collated_1"][0].swap())) == 1
        assert not list(fanout.full_queues())


class TestSweeper:
    async def test_full_queues(self):
        full_fanout = MagicMock(spec=Fanout)
        full_fanout.full_queues.side_effect = lambda: iter(
            [
                (
                    Queue(0, 0, None),
                    TableConfig(name="full", timestamp=True, include_routing_key=False),
                )
            ]
        )
        full_fanout.queues.return_value = {}

        result = list(Sweeper(60).tick(full_fanout))
        assert compact(result) == [
            Table(
                TableConfig(name="full", timestamp=True, include_routing_key=False), []
            )
        ]

    def test_iter_over_queues(self):
        fanout = MagicMock(spec=Fanout)
        fanout.full_queues.return_value = iter([])
        q1 = Queue[tuple[bytes | None], None](0, 0, (None,))
        q2 = Queue[tuple[bytes | None], None](0, 0, (None,))
        q1.insert((b"a",))
        q2.insert((b"b",))
        queues = {
            "a": (
                q1,
                TableConfig(name="a", timestamp=True, include_routing_key=False),
            ),
            "b": (
                q2,
                TableConfig(name="b", timestamp=True, include_routing_key=False),
            ),
        }
        fanout.queues = queues

        sweeper = Sweeper(60)
        result = sweeper.tick(fanout)
        assert next(result) == Table(
            TableConfig(name="a", timestamp=True, include_routing_key=False),
            [(b"a",)],  # type: ignore
        )
        with pytest.raises(StopIteration):
            next(result)
        queues.clear()
        result = sweeper.tick(fanout)
        assert next(result) == Table(
            TableConfig(name="b", timestamp=True, include_routing_key=False),
            [(b"b",)],  # type: ignore
        )
        with pytest.raises(StopIteration):
            next(result)
        result = sweeper.tick(fanout)
        with pytest.raises(StopIteration):
            next(result)


class TestSink:
    @pytest.mark.parametrize(
        "config,cols",
        [
            (
                TableConfig(name="test", timestamp=False, include_routing_key=False),
                ["a", "b"],
            ),
            (
                TableConfig(name="test", timestamp=False, include_routing_key=True),
                ["a", "b", "routing_key"],
            ),
            (
                TableConfig(name="test", timestamp=True, include_routing_key=False),
                ["a", "b", "timestamp"],
            ),
            (
                TableConfig(name="test", timestamp=True, include_routing_key=True),
                ["a", "b", "routing_key", "timestamp"],
            ),
        ],
    )
    async def test_sink(self, config: TableConfig, cols: list[str]):
        catalog = MagicMock(spec=Catalog)
        sink = Sink(catalog, asyncio.get_event_loop())
        table = MagicMock(spec=IcebergTable)
        catalog.create_table_if_not_exists.return_value = table

        sink.write(
            Table(
                config,
                [
                    (b'{"a": 1, "b": 2}', "routing_key_1", datetime(2024, 1, 1), 0),
                    (b'{"a": 2, "b": 3}', "routing_key_1", datetime(2024, 1, 1), 1),
                ],
            )
        )
        schema = (
            pl.DataFrame(
                [],
                schema={
                    "a": pl.Int64,
                    "b": pl.Int64,
                    "timestamp": pl.Datetime,
                    "routing_key": pl.Utf8,
                },
            )
            .select(cols)
            .to_arrow()
            .schema
        )
        catalog.create_table_if_not_exists.assert_called_once()
        assert catalog.create_table_if_not_exists.call_args.args[0] == config.name
        assert catalog.create_table_if_not_exists.call_args.kwargs["schema"] == schema
        table.append.assert_called_once()
        assert table.append.call_args.args[0].column_names == cols
        assert len(table.append.call_args.args[0]) == 2
