from contextlib import nullcontext
from datetime import UTC, datetime, timedelta

import pytest

from thrs.monitoring.bins import (
    BIN_SIZES,
    MAX_POINTS,
    InvalidRangeError,
    bin_size,
    requested_bin,
    validate_range,
)

START = datetime(2026, 11, 10, tzinfo=UTC)


@pytest.mark.parametrize(
    ("span", "expected"),
    [
        (timedelta(minutes=5), timedelta(seconds=1)),
        (timedelta(hours=1), timedelta(seconds=10)),
        (timedelta(hours=6), timedelta(minutes=1)),
        (timedelta(hours=24), timedelta(minutes=5)),
        (timedelta(days=7), timedelta(minutes=30)),
        (timedelta(days=30), timedelta(hours=3)),
    ],
)
def test_bin_size_picks_the_smallest_round_bin_within_max_points(span, expected):
    assert bin_size(START, START + span) == expected


def test_bin_size_never_exceeds_max_points_for_the_longest_range():
    span = timedelta(days=30)
    assert span / bin_size(START, START + span) <= MAX_POINTS


def test_bin_size_falls_back_to_the_largest_bin():
    assert bin_size(START, START + timedelta(days=3650)) == BIN_SIZES[-1]


@pytest.mark.parametrize(
    ("span", "expectation"),
    [
        (timedelta(hours=6), nullcontext()),
        (timedelta(days=30), nullcontext()),
        (timedelta(days=30, seconds=1), pytest.raises(InvalidRangeError)),
        (timedelta(0), pytest.raises(InvalidRangeError)),
        (timedelta(hours=-1), pytest.raises(InvalidRangeError)),
    ],
)
def test_validate_range(span, expectation):
    with expectation:
        validate_range(START, START + span)


def test_requested_bin_accepts_only_round_bins_within_max_points():
    assert requested_bin(START, START + timedelta(hours=1), 300) == timedelta(minutes=5)
    with pytest.raises(InvalidRangeError):
        requested_bin(START, START + timedelta(hours=1), 7)
    with pytest.raises(InvalidRangeError):
        requested_bin(START, START + timedelta(days=30), 1)
