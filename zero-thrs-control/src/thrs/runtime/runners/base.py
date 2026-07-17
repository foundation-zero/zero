from typing import Protocol


class Runner(Protocol):
    async def tick(self) -> None: ...
