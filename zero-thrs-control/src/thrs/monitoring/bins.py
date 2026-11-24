from datetime import datetime, timedelta

MAX_POINTS = 400
MAX_RANGE = timedelta(days=30)

BIN_SIZES = tuple(
    timedelta(seconds=seconds)
    for seconds in (1, 5, 10, 30, 60, 300, 600, 1800, 3600, 10800, 21600, 43200, 86400)
)


class InvalidRangeError(ValueError):
    pass


def validate_range(start: datetime, end: datetime) -> None:
    if end <= start:
        raise InvalidRangeError("The range must end after it starts")
    if end - start > MAX_RANGE:
        raise InvalidRangeError(f"The range may span at most {MAX_RANGE.days} days")


def requested_bin(start: datetime, end: datetime, seconds: int) -> timedelta:
    """A bin the client asks for, e.g. to refresh the tail of a range it already shows."""
    size = timedelta(seconds=seconds)
    if size not in BIN_SIZES:
        raise InvalidRangeError(
            f"binSeconds must be one of {[int(b.total_seconds()) for b in BIN_SIZES]}"
        )
    if (end - start) / size > MAX_POINTS:
        raise InvalidRangeError(f"binSeconds gives more than {MAX_POINTS} points")
    return size


def bin_size(start: datetime, end: datetime) -> timedelta:
    """The smallest round bin that keeps a series at or below MAX_POINTS."""
    span = end - start
    return next(
        (size for size in BIN_SIZES if span / size <= MAX_POINTS), BIN_SIZES[-1]
    )
