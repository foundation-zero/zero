from typing import Protocol


class Runner(Protocol):
    async def run(self, n_ticks: int) -> None: ...
