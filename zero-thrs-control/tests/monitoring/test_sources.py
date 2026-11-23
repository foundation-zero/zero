import re

import pytest

from thrs.monitoring.sources import (
    SERIES_SOURCES,
    STATE_SOURCES,
    MonitoringMetric,
    MonitoringModule,
    MonitoringSignal,
    ParameterSource,
    UnsupportedSignalError,
    state_source,
)

# Names are interpolated into SQL, so they must stay plain identifiers.
IDENTIFIER = re.compile(r"^[a-z0-9_]+$")


def test_every_metric_has_a_source():
    assert set(SERIES_SOURCES) == set(MonitoringMetric)


def test_every_dhw_signal_has_a_source():
    assert set(STATE_SOURCES[MonitoringModule.DHW]) == set(MonitoringSignal)


@pytest.mark.parametrize("metric", list(MonitoringMetric))
def test_series_sources_are_plain_identifiers(metric):
    source = SERIES_SOURCES[metric]
    table = (
        source.table(MonitoringModule.DHW)
        if isinstance(source, ParameterSource)
        else source.table
    )

    assert IDENTIFIER.match(table)
    assert IDENTIFIER.match(source.column)


@pytest.mark.parametrize("signal", list(MonitoringSignal))
def test_state_sources_are_plain_identifiers(signal):
    source = state_source(MonitoringModule.DHW, signal)

    assert IDENTIFIER.match(source.table)
    assert IDENTIFIER.match(source.column)


def test_modes_map_null_to_manual():
    assert (
        state_source(MonitoringModule.DHW, MonitoringSignal.BOOSTING_MODE).null_state
        == "manual"
    )
    assert (
        state_source(MonitoringModule.DHW, MonitoringSignal.TANK_1_STATE).null_state
        is None
    )


def test_unknown_signal_for_a_module_raises(monkeypatch):
    monkeypatch.setitem(STATE_SOURCES, MonitoringModule.DHW, {})

    with pytest.raises(UnsupportedSignalError):
        state_source(MonitoringModule.DHW, MonitoringSignal.BOOSTING_MODE)


def test_amcs_modes_are_named():
    source = state_source(MonitoringModule.DHW, MonitoringSignal.AMCS_MODE)

    assert [source.state(value) for value in (0, 1, 2, 3, None)] == [
        "amcs_local",
        "amcs_manual",
        "amcs_auto",
        "advisory",
        None,
    ]
