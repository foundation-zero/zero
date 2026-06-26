import inspect
from typing import Callable, Concatenate, assert_never, cast, overload

from aiomqtt import Message, Client as MqttClient
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


@dataclass
class Publishable[M: BaseModel]:
    contents: M
    topic: str
    qos: int
    retain: bool

    async def publish(self, client: MqttClient):
        await client.publish(
            self.topic,
            self.contents.model_dump_json(by_alias=True),
            qos=self.qos,
            retain=self.retain,
        )


def extract_topic_params(format: str, topic: str) -> dict[str, str]:
    format_parts = format.split("/")
    topic_parts = topic.split("/")

    if len(format_parts) != len(topic_parts):
        raise ValueError(
            f"Format and topic do not have the same number of parts: {format} vs {topic}"
        )

    for format_part, topic_part in zip(format_parts, topic_parts):
        if not format_part.startswith(":") and format_part != topic_part:
            raise ValueError(f"Format and topic do not match: {format} vs {topic}")

    return {
        format_part[1:]: topic_part
        for format_part, topic_part in zip(format_parts, topic_parts)
        if format_part.startswith(":")
    }


def inject_topic_params(format: str, topic_params: dict[str, str]) -> str:
    format_parts = format.split("/")

    def _resolve_part(format_part: str) -> str:
        if format_part.startswith(":"):
            param_name = format_part[1:]
            if param_name not in topic_params:
                raise ValueError(f"Missing topic parameter: {param_name}")
            return topic_params[param_name]
        else:
            return format_part

    topic_parts = [_resolve_part(part) for part in format_parts]
    return "/".join(topic_parts)


def format_to_wildcard(format: str) -> str:
    format_parts = format.split("/")
    wildcard_parts = ["+" if part.startswith(":") else part for part in format_parts]
    return "/".join(wildcard_parts)


class Route[M: BaseModel]:
    def __init__(
        self,
        topic_format: str,
        cls: type[M],
        qos: int,
        retain: bool,
    ):
        self._topic_format = topic_format
        self._cls = cls
        self._qos = qos
        self._retain = retain

    @property
    def cls(self) -> type[M]:
        return self._cls

    @property
    def topic_format(self) -> str:
        return self._topic_format

    @property
    def qos(self) -> int:
        return self._qos


class Handler[M: BaseModel, C, **P](Route[M]):
    def __init__(
        self,
        topic_format: str,
        cls: type[M],
        handler: Callable[Concatenate[M, C, P], None],
        qos: int,
        retain: bool,
    ):
        super().__init__(topic_format, cls, qos, retain)
        self._handler = handler

    @property
    def handler(self) -> Callable[Concatenate[M, C, P], None]:
        return self._handler

    def __call__(self, message: M, context: C, topic: str):
        topic_params = extract_topic_params(self._topic_format, topic)
        handler = cast(Callable[..., None], self._handler)
        handler(message, context, **topic_params)

    def construct(
        self,
        app: "MessagingDefinition[M, C]",
        contents: M,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Publishable[M]:
        prefixed_topic = app.lookup_prefixed_topic(self)
        if prefixed_topic is None:
            raise ValueError(
                f"Handler {self._handler} for message type {self._cls} is not registered with the router"
            )

        arg_names = list(inspect.signature(self._handler).parameters.keys())[2:]
        return Publishable(
            contents=contents,
            topic=inject_topic_params(
                prefixed_topic,
                {
                    **dict(zip(arg_names, [str(arg) for arg in args])),
                    **{k: str(v) for k, v in kwargs.items()},
                },
            ),
            qos=self._qos,
            retain=self._retain,
        )


class MessageRouter[M: BaseModel, C]:
    def __init__(
        self,
        type_resolver: Callable[[type[M], C], type[M]] = lambda message_type,
        context: message_type,
    ):
        self._handlers: list[Handler[M, C, ...]] = []
        self._routes: list[Route[M]] = []
        self._type_resolver = type_resolver

    @overload
    def handle[**P](
        self,
        topic_format: str,
        message_type: type[M],
        qos=1,
        retain=False,
    ) -> Callable[[Callable[Concatenate[M, C, P], None]], Handler[M, C, P]]: ...

    @overload
    def handle[**P](
        self,
        route: Route[M],
    ) -> Callable[[Callable[Concatenate[M, C, P], None]], Handler[M, C, P]]: ...

    def handle[**P](
        self,
        topic_format_or_definition: "str | MessagingDefinition[M, object]",
        message_type_or_route: type[M] | Route[M],
        qos=1,
        retain=False,
    ) -> Callable[[Callable[Concatenate[M, C, P], None]], Handler[M, C, P]]:
        if isinstance(topic_format_or_definition, str) and isinstance(
            message_type_or_route, type
        ):
            topic_format = topic_format_or_definition
            message_type = message_type_or_route
            route = Route(topic_format, message_type, qos, retain)
        elif isinstance(topic_format_or_definition, MessagingDefinition) and isinstance(
            message_type_or_route, Route
        ):
            definition = topic_format_or_definition
            route = message_type_or_route
            topic_format = route.topic_format
            message_type = route.cls
        else:
            raise TypeError(
                "Invalid arguments to handle: expected (str, type) or (MessagingDefinition, Route)"
            )

        def decorator(
            handler: Callable[Concatenate[M, C, P], None],
        ) -> Handler[M, C, P]:
            new_handler = Handler(topic_format, message_type, handler, qos, retain)
            self._handlers.append(new_handler)
            return new_handler

        return decorator

    def define(
        self,
        topic_format: str,
        message_type: type[M],
        qos=1,
        retain=False,
    ) -> Route[M]:
        route = Route(topic_format, message_type, qos, retain)
        self._routes.append(route)
        return route

    @property
    def handlers(self) -> list[Handler[M, C, ...]]:
        return self._handlers

    def delegate(self, prefix: str, handler: "MessageRouter[M, C]"):
        self._handlers.extend(
            Handler(f"{prefix}/{h.topic_format}", h.cls, h._handler, h.qos, h._retain)
            for h in handler.handlers
        )

    def lookup_prefixed_topic(self, handler: Handler) -> str | None:
        return next(
            (
                handler.topic_format
                for mine in self._handlers
                if handler.cls == mine.cls and handler.handler == mine.handler
            ),
            None,
        )

    def execute(self, message: Message, context: C):
        for handler in self._handlers:
            if message.topic.matches(format_to_wildcard(handler.topic_format)):
                resolved_type = self._type_resolver(handler.cls, context)
                if not isinstance(message.payload, bytes | str):
                    raise ValueError(
                        f"Expected payload to be bytes or str, got {type(message.payload)}"
                    )
                handler(
                    resolved_type.model_validate_json(message.payload),
                    context,
                    message.topic.value,
                )
                break

    async def subscribe(self, client: MqttClient):
        for handler in self._handlers:
            await client.subscribe(format_to_wildcard(handler.topic_format), qos=1)


class MessagingDefinition[M: BaseModel, C](MessageRouter[M, C]):
    def mirror(
        self, type_resolver: Callable[[type[M], object], type[M]]
    ) -> "MessageRouter[M, object]":
        return MessageRouter(type_resolver=type_resolver)
