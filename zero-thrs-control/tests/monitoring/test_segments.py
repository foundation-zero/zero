from datetime import UTC, datetime, timedelta

from thrs.monitoring.segments import Sample, Segment, merge_segments, state_totals

START = datetime(2026, 11, 10, 12, tzinfo=UTC)
END = START + timedelta(hours=1)


def at(minutes: float) -> datetime:
    return START + timedelta(minutes=minutes)


def sample(minutes: float, state: str | None) -> Sample:
    return Sample(timestamp=at(minutes), state=state)


def test_no_samples_gives_no_segments():
    assert merge_segments([], START, END) == []


def test_state_before_the_range_opens_it():
    segments = merge_segments(
        [sample(-30, "idle"), sample(10, "filling"), sample(59, "filling")], START, END
    )

    assert segments == [
        Segment(state="idle", start=START, end=at(10)),
        Segment(state="filling", start=at(10), end=END),
    ]


def test_repeated_states_merge_into_one_segment():
    segments = merge_segments(
        [sample(0, "idle"), sample(20, "idle"), sample(59, "idle")], START, END
    )

    assert segments == [Segment(state="idle", start=START, end=END)]


def test_null_maps_to_the_null_state():
    segments = merge_segments(
        [sample(0, "boosting_heatpump"), sample(15, None), sample(59, None)],
        START,
        END,
        null_state="manual",
    )

    assert segments == [
        Segment(state="boosting_heatpump", start=START, end=at(15)),
        Segment(state="manual", start=at(15), end=END),
    ]


def test_null_without_a_null_state_leaves_a_gap():
    segments = merge_segments(
        [
            sample(0, "in use"),
            sample(15, None),
            sample(30, "filling"),
            sample(59, "filling"),
        ],
        START,
        END,
    )

    assert segments == [
        Segment(state="in use", start=START, end=at(15)),
        Segment(state="filling", start=at(30), end=END),
    ]


def test_a_signal_that_stopped_reporting_ends_at_its_last_sample():
    segments = merge_segments([sample(0, "idle"), sample(20, "idle")], START, END)

    assert segments == [Segment(state="idle", start=START, end=at(20))]


def test_a_recent_last_sample_runs_on_to_the_end():
    segments = merge_segments([sample(0, "idle"), sample(57, "idle")], START, END)

    assert segments == [Segment(state="idle", start=START, end=END)]


def test_a_single_opening_sample_that_is_stale_gives_nothing():
    assert merge_segments([sample(-30, "idle")], START, END) == []


def test_state_totals_sum_per_state():
    segments = [
        Segment(state="idle", start=START, end=at(10)),
        Segment(state="filling", start=at(10), end=at(25)),
        Segment(state="idle", start=at(25), end=END),
    ]

    assert state_totals(segments) == {
        "idle": timedelta(minutes=45),
        "filling": timedelta(minutes=15),
    }
