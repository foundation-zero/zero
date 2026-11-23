from collections import defaultdict
from datetime import datetime, timedelta

from pydantic import BaseModel

# Without a sample for this long, a signal is treated as no longer reporting.
STALE_AFTER = timedelta(minutes=5)


class Sample(BaseModel, frozen=True):
    timestamp: datetime
    state: str | None


class Segment(BaseModel, frozen=True):
    state: str
    start: datetime
    end: datetime

    @property
    def duration(self) -> timedelta:
        return self.end - self.start


def merge_segments(
    samples: list[Sample],
    start: datetime,
    end: datetime,
    null_state: str | None = None,
) -> list[Segment]:
    """Turn change-point samples into segments clipped to [start, end].

    `samples` are ordered by time. The first may lie before `start`: it holds
    the state the range opens with. The last is the latest sample, so a signal
    that stopped reporting ends there instead of running on to `end`.
    """
    if not samples:
        return []

    last_sample = samples[-1].timestamp
    close = end if end - last_sample <= STALE_AFTER else min(end, last_sample)

    boundaries = [*(sample.timestamp for sample in samples[1:]), close]
    raw = [
        Segment(state=state, start=max(sample.timestamp, start), end=boundary)
        for sample, boundary in zip(samples, boundaries, strict=True)
        if (state := sample.state if sample.state is not None else null_state)
        is not None
        and boundary > max(sample.timestamp, start)
    ]

    merged: list[Segment] = []
    for segment in raw:
        if (
            merged
            and merged[-1].state == segment.state
            and merged[-1].end == segment.start
        ):
            merged[-1] = merged[-1].model_copy(update={"end": segment.end})
        else:
            merged.append(segment)
    return merged


def state_totals(segments: list[Segment]) -> dict[str, timedelta]:
    totals: defaultdict[str, timedelta] = defaultdict(timedelta)
    for segment in segments:
        totals[segment.state] += segment.duration
    return dict(totals)
