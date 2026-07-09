from typing import Protocol


class Runner(Protocol):
    async def run(self) -> None: ...
