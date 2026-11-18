"""Hourly electrical energy per consumer on Zero's 700 V, 400 V, 350 V and 24 V buses over weekends."""

import csv
import json
import re
import statistics
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import NamedTuple
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict

GREPTIME_SQL_URL = "http://greptime-zero.tail0b4840.ts.net:4000/v1/sql?db=public"
SHIP_TIME = ZoneInfo("Europe/Amsterdam")
HERE = Path(__file__).parent
OUT = HERE / "out"
METADATA_CSV = HERE / "marpower_device_metadata.csv"
SATURDAYS = [date(2026, 10, 31), date(2026, 11, 7), date(2026, 11, 14)]
TOP_SERIES_PER_CHART = 12
BUSES = ["700V", "400V", "350V", "24V"]
BUS_TITLES = {
    "700V": "700 V DC",
    "400V": "400 V AC",
    "350V": "350 V DC",
    "24V": "24 V DC",
}
SWITCH_PANEL = "700V switches"
CHART_TITLES = {
    **{
        f"{bus} {side}": f"{title} {side}"
        for bus, title in BUS_TITLES.items()
        for side in ("consumers", "suppliers")
    },
    SWITCH_PANEL: "700 V DC switch flows",
}


class Weekend(BaseModel):
    model_config = ConfigDict(frozen=True)

    saturday: date

    @property
    def sunday(self) -> date:
        return self.saturday + timedelta(days=1)

    @property
    def slug(self) -> str:
        return f"{self.saturday.isoformat()}_{self.sunday.isoformat()}"

    @property
    def label(self) -> str:
        if self.saturday.month == self.sunday.month:
            return f"{self.saturday.day}–{self.sunday.day} {self.sunday:%b %Y}"
        return f"{self.saturday.day} {self.saturday:%b} – {self.sunday.day} {self.sunday:%b %Y}"

    @property
    def start(self) -> datetime:
        return datetime(
            self.saturday.year, self.saturday.month, self.saturday.day, tzinfo=SHIP_TIME
        )

    @property
    def hours(self) -> list[datetime]:
        return [
            (self.start.astimezone(ZoneInfo("UTC")) + timedelta(hours=h)).astimezone(
                SHIP_TIME
            )
            for h in range(48)
        ]

    def sql_filter(self) -> str:
        start_utc = self.start.astimezone(ZoneInfo("UTC"))
        end_utc = start_utc + timedelta(hours=48)
        return f"timestamp >= '{start_utc:%Y-%m-%dT%H:%M:%SZ}' AND timestamp < '{end_utc:%Y-%m-%dT%H:%M:%SZ}'"


class Series(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str
    bus: str
    role: str
    name: str
    technical_name: str
    direction: str
    source: str

    @property
    def label(self) -> str:
        return (
            f"{self.name} - {self.technical_name}" if self.name else self.technical_name
        )

    @property
    def header(self) -> str:
        prefix = self.bus if self.role == "consumer" else f"{self.bus} {self.role}"
        return " | ".join(part for part in [prefix, self.label, self.direction] if part)


def series(
    key: str,
    bus: str,
    role: str,
    name: str,
    technical_name: str,
    direction: str,
    source: str,
) -> Series:
    return Series(
        key=key,
        bus=bus,
        role=role,
        name=name,
        technical_name=technical_name,
        direction=direction,
        source=source,
    )


def query(sql: str) -> list[list]:
    body = urllib.parse.urlencode({"sql": sql}).encode()
    with urllib.request.urlopen(GREPTIME_SQL_URL, body, timeout=900) as response:
        result = json.load(response)
    if "output" not in result:
        raise RuntimeError(f"Greptime error: {result}\n{sql}")
    return result["output"][0]["records"]["rows"]


def hour_bin() -> str:
    return "date_bin('1 hour'::INTERVAL, timestamp, TIMESTAMP '1970-01-01')"


def load_names() -> dict[str, str]:
    with METADATA_CSV.open() as handle:
        return {
            row["technical_name"]: row["name"]
            for row in csv.DictReader(handle)
            if row["system"] != "45-pms"
        }


def positive_part(expression: str) -> str:
    return f"avg(CASE WHEN {expression} > 0 THEN {expression} ELSE 0 END)"


def negative_part(expression: str) -> str:
    return f"avg(CASE WHEN {expression} < 0 THEN -({expression}) ELSE 0 END)"


Source = tuple[str, list[tuple[str, list[Series]]]]


def sources(
    weekend: Weekend, names: dict[str, str], tag_rows: list[list]
) -> list[Source]:
    """Each source is a query returning (hour, key, value in W, ...) rows, with the series each value column fills per key."""
    where = weekend.sql_filter()
    return [
        *ugrid_inverters(where, names),
        brightloops(where, names),
        *epic_converters(where, names),
        shore_converters(where),
        dc_switches(where),
        ac_meters(where, names),
        power_tags(where, tag_rows),
        weidmullers(where),
        leuze_modules(where, names),
    ]


def ugrid_inverters(where: str, names: dict[str, str]) -> list[Source]:
    tables = {
        "05-11-u101": "marpower__450000_dynamic_conv_ps_ara__5_11_u101",
        "05-12-u101": "marpower__450000_dynamic_conv_sb_ara__5_12_u101",
    }
    return [
        (
            f"SELECT {hour_bin()}, '{technical}', avg(pv_power__value) * 1000 FROM {table} WHERE {where} GROUP BY 1",
            [
                (
                    technical,
                    [
                        series(
                            f"inverter:{technical}",
                            "700V",
                            "consumer",
                            f"ugrid {names.get(technical, '')}".strip(),
                            technical,
                            "",
                            f"{table}.pv_power (kW) × 1000",
                        )
                    ],
                )
            ],
        )
        for technical, table in tables.items()
    ]


def brightloops(where: str, names: dict[str, str]) -> Source:
    table = "marpower__450000_main_power_storage_errors"
    sql = (
        f"SELECT {hour_bin()}, topic, "
        f"avg(CASE WHEN charging__value THEN pv_power__value ELSE 0 END) * 1000, "
        f"avg(CASE WHEN charging__value THEN 0 ELSE pv_power__value END) * 1000 "
        f"FROM {table} WHERE {where} GROUP BY 1, 2"
    )
    packs = [
        f"05-{bank}-{index}"
        for bank, count in [(41, 4), (42, 3), (43, 3), (44, 4), (45, 4), (46, 4)]
        for index in range(1, count + 1)
    ]
    return (
        sql,
        [
            (
                f"marpower/450000-main-power-storage-errors/{pack[1:]}",
                [
                    series(
                        f"brightloop-in:{pack}",
                        "700V",
                        "consumer",
                        brightloop_name(names, pack),
                        pack,
                        "to battery",
                        f"{table}.pv_power (kW) × 1000 while charging",
                    ),
                    series(
                        f"brightloop-out:{pack}",
                        "700V",
                        "source",
                        brightloop_name(names, pack),
                        pack,
                        "from battery",
                        f"{table}.pv_power (kW) × 1000 while not charging",
                    ),
                ],
            )
            for pack in packs
        ],
    )


def brightloop_name(names: dict[str, str], pack: str) -> str:
    return f"brightloop {names.get(pack, '')}".strip()


def epic_converters(where: str, names: dict[str, str]) -> list[Source]:
    devices = {
        "02-71-t101": (
            "marpower/busbar/epc-71-t101",
            "marpower__450000_dc_distribution__350v_conv_aft_1",
        ),
        "02-71-t102": (
            "marpower/busbar/epc-71-t102",
            "marpower__450000_dc_distribution__350v_conv_aft_2",
        ),
        "02-72-t101": (
            "marpower/busbar/epc-72-t101",
            "marpower__450000_dc_distribution__350v_conv_fwd_1",
        ),
        "02-72-t102": (
            "marpower/busbar/epc-72-t102",
            "marpower__450000_dc_distribution__350v_conv_fwd_2",
        ),
    }
    return [
        (
            f"SELECT {hour_bin()}, '{technical}', {positive_part('hvdc_power__value')}, {negative_part('hvdc_power__value')}, "
            f"{positive_part('lvdc_voltage__value * lvdc_current__value')}, {negative_part('lvdc_voltage__value * lvdc_current__value')} FROM ("
            f"SELECT timestamp, hvdc_power__value, lvdc_voltage__value, lvdc_current__value FROM marpower__busbar WHERE {where} AND topic = '{busbar_topic}' "
            f"UNION ALL SELECT timestamp, hvdc_power__value, lvdc_voltage__value, lvdc_current__value FROM {table} WHERE {where}) GROUP BY 1",
            [
                (
                    technical,
                    [
                        series(
                            f"epic-in:{technical}",
                            "700V",
                            "consumer",
                            f"epic {names.get(technical, '')}".strip(),
                            technical,
                            "to 350V",
                            "hvdc_power (W)",
                        ),
                        series(
                            f"epic-out:{technical}",
                            "700V",
                            "source",
                            f"epic {names.get(technical, '')}".strip(),
                            technical,
                            "from 350V",
                            "hvdc_power (W)",
                        ),
                        series(
                            f"epic-350v-out:{technical}",
                            "350V",
                            "source",
                            f"epic {names.get(technical, '')}".strip(),
                            technical,
                            "to 350V",
                            "lvdc_voltage × lvdc_current (W)",
                        ),
                        series(
                            f"epic-350v-in:{technical}",
                            "350V",
                            "consumer",
                            f"epic {names.get(technical, '')}".strip(),
                            technical,
                            "from 350V",
                            "lvdc_voltage × lvdc_current (W)",
                        ),
                    ],
                )
            ],
        )
        for technical, (busbar_topic, table) in devices.items()
    ]


def shore_converters(where: str) -> Source:
    table = "marpower__450000_dc_distribution_esi"
    technical_names = ["07-11-tbc1a", "07-11-tbc1b", "07-12-tbc1a", "07-12-tbc1b"]
    return (
        f"SELECT {hour_bin()}, topic, avg(esi_ac_bus_active_power_3_phase__value) * 1000 FROM {table} WHERE {where} AND topic LIKE '%/07-1%' GROUP BY 1, 2",
        [
            (
                f"marpower/450000-dc-distribution-esi/{technical}",
                [
                    series(
                        f"shore:{technical}",
                        "700V",
                        "source",
                        "shore converter",
                        technical,
                        "",
                        f"{table}.esi_ac_bus_active_power_3_phase (kW) × 1000",
                    )
                ],
            )
            for technical in technical_names
        ],
    )


def dc_switches(where: str) -> Source:
    table = "marpower__450000_dc_distribution__dc_switch"
    power = "dcv_s_0__value * dcc_s_0__value"
    topics = [
        "keb6-0571",
        "keb6-0572",
        "keb6-0573",
        "keb7-0574",
        "keb7-0575",
        "keb8-0576",
        "keb8-0577",
        "keb9-0578",
    ]
    return (
        f"SELECT {hour_bin()}, topic, {positive_part(power)}, {negative_part(power)} FROM {table} WHERE {where} AND topic LIKE '%/dc-switch/keb%' GROUP BY 1, 2",
        [
            (
                f"marpower/450000-dc-distribution/dc-switch/{topic}",
                [
                    series(
                        f"switch-pos:{topic}",
                        "700V",
                        "flow",
                        "",
                        f"05-{topic[-2:]}-q101",
                        "positive current",
                        f"{table}.dcv_s_0 × dcc_s_0",
                    ),
                    series(
                        f"switch-neg:{topic}",
                        "700V",
                        "flow",
                        "",
                        f"05-{topic[-2:]}-q101",
                        "negative current",
                        f"{table}.dcv_s_0 × dcc_s_0",
                    ),
                ],
            )
            for topic in topics
        ],
    )


def ac_meters(where: str, names: dict[str, str]) -> Source:
    meters = {
        "10p0-1-100q01": "marpower__450000_dynamic_conv_ps_general",
        "10p0-3-300q01": "marpower__450000_dynamic_conv_sb_general",
    }
    sql = " UNION ALL ".join(
        f"SELECT {hour_bin()}, '{technical}', avg(totalactivepower__value) FROM {table} WHERE {where} GROUP BY 1"
        for technical, table in meters.items()
    )
    return (
        sql,
        [
            (
                technical,
                [
                    series(
                        f"acmeter:{technical}",
                        "400V",
                        "source",
                        f"ugrid {names.get(technical, '')}".strip(),
                        technical,
                        "",
                        f"{table}.totalactivepower (W)",
                    )
                ],
            )
            for technical, table in meters.items()
        ],
    )


def power_tag_rows() -> list[list]:
    return query(
        "SELECT DISTINCT topic, panel, component, consumer FROM power_tags "
        "WHERE timestamp >= '2026-10-30T00:00:00Z' AND timestamp < '2026-11-16T00:00:00Z' AND coalesce(component, '') NOT IN ('135Q01', '335Q01')"
    )


def power_tags(where: str, rows: list[list]) -> Source:
    return (
        f"SELECT {hour_bin()}, topic, avg(active_power_total) FROM power_tags WHERE {where} AND coalesce(component, '') NOT IN ('135Q01', '335Q01') GROUP BY 1, 2",
        [
            (
                topic,
                [
                    series(
                        f"powertag:{topic}",
                        "400V",
                        "consumer",
                        "10p3 (feeder)" if component == "336Q01" else consumer.lower(),
                        f"{panel} {component}".strip(),
                        "",
                        "power_tags.active_power_total (W)",
                    )
                ],
            )
            for topic, panel, component, consumer in sorted(
                rows, key=lambda row: row[0]
            )
        ],
    )


WEIDMULLER_TECHNICAL_NAMES = {
    "w14e1-01v01": "14e1-01v01",
    "w14e1-01v02": "14e1-01v02",
    "w14e1-02v01": "14e1-02v01",
    "w14e1-02v02": "14e1-02v02",
    "w14e1-03v01": "14e1-01v03",
    "w14e1-03v02": "14e1-02v03",
    "w14e2-01v01": "14e2-01v01",
    "w14e2-01v02": "14e2-01v02",
    "w14e2-01v03": "14e2-01v03",
    "w14e2-02v01": "14e2-02v01",
    "w14e2-02v02": "14e2-02v02",
}


def weidmullers(where: str) -> Source:
    table = "marpower__450000_24vdc_system"
    return (
        f"SELECT {hour_bin()}, topic, avg(power__value) FROM {table} WHERE {where} AND topic LIKE '%/conv/w14e%' GROUP BY 1, 2",
        [
            (
                f"marpower/450000-24vdc-system/conv/{old}",
                [
                    series(
                        f"weidmuller:{old}",
                        "24V",
                        "source",
                        "power supply",
                        technical,
                        "",
                        f"{table}.power (W)",
                    )
                ],
            )
            for old, technical in WEIDMULLER_TECHNICAL_NAMES.items()
        ],
    )


def leuze_modules(where: str, names: dict[str, str]) -> Source:
    table = "marpower__450000_24vdc_system"
    modules = sorted(
        technical
        for technical in names
        if re.fullmatch(r"14e[123]-\d\df\d\d", technical)
    )
    sql = (
        f"WITH voltages AS (SELECT {hour_bin()} AS hour, CASE WHEN topic LIKE '%/w14e1-%' THEN '14e1' ELSE '14e2' END AS bus, avg(voltage__value) AS voltage "
        f"FROM {table} WHERE {where} AND topic LIKE '%/conv/w14e%' AND voltage__value > 0 GROUP BY 1, 2), "
        f"currents AS (SELECT {hour_bin()} AS hour, topic, CASE WHEN topic LIKE '%/14e1-%' THEN '14e1' ELSE '14e2' END AS bus, avg(output_current__value) / 1000.0 AS current "
        f"FROM {table} WHERE {where} AND topic LIKE 'marpower/450000-24vdc-system/14e%' GROUP BY 1, 2, 3) "
        f"SELECT c.hour, c.topic, c.current * v.voltage FROM currents c JOIN voltages v ON c.hour = v.hour AND c.bus = v.bus"
    )
    return (
        sql,
        [
            (
                f"marpower/450000-24vdc-system/{technical}",
                [
                    series(
                        f"leuze:{technical}",
                        "24V",
                        "consumer",
                        names.get(technical, ""),
                        technical,
                        "",
                        f"{table}.output_current (mA) / 1000 × supply voltage",
                    )
                ],
            )
            for technical in modules
        ],
    )


def collect(
    weekend: Weekend, names: dict[str, str], tag_rows: list[list]
) -> dict[Series, dict[datetime, float]]:
    weekend_sources = sources(weekend, names, tag_rows)
    readings = [
        (series, to_ship_time(row[0]), value / 1000)
        for sql, mapping in weekend_sources
        for row in query(sql)
        for series, value in zip(dict(mapping).get(row[1], []), row[2:])
        if value is not None
    ]
    kwh_by_series: dict[Series, dict[datetime, float]] = {
        series: {}
        for _, mapping in weekend_sources
        for _, series_list in mapping
        for series in series_list
    }
    for series, hour, kwh in readings:
        kwh_by_series[series][hour] = kwh
    return kwh_by_series


def to_ship_time(epoch: int) -> datetime:
    return datetime.fromtimestamp(
        epoch / 1e9 if epoch > 1e14 else epoch / 1e3, ZoneInfo("UTC")
    ).astimezone(SHIP_TIME)


Profile = dict[Series, list[float | None]]


class Period(NamedTuple):
    slug: str
    label: str
    hours: list[str]
    values: Profile


def weekend_period(
    weekend: Weekend, kwh: dict[Series, dict[datetime, float]], series: list[Series]
) -> Period:
    return Period(
        weekend.slug,
        weekend.label,
        [hour.isoformat() for hour in weekend.hours],
        {item: [kwh[item].get(hour) for hour in weekend.hours] for item in series},
    )


def average_period(periods: list[Period], series: list[Series]) -> Period:
    def hour_mean(item: Series, hour: int) -> float | None:
        samples = [
            value
            for period in periods
            for day in (0, 1)
            if (value := period.values[item][day * 24 + hour]) is not None
        ]
        return statistics.mean(samples) if samples else None

    return Period(
        "average",
        "Average",
        [f"{hour:02d}:00" for hour in range(24)],
        {item: [hour_mean(item, hour) for hour in range(24)] for item in series},
    )


def total(values: list[float | None]) -> float:
    return sum(value for value in values if value is not None)


def energy_unit(bus: str) -> tuple[str, float]:
    return ("Wh", 1000.0) if bus == "24V" else ("kWh", 1.0)


def write_csv(path: Path, period: Period, series: list[Series]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time (ship time)",
                *[f"{item.header} [{energy_unit(item.bus)[0]}]" for item in series],
            ]
        )
        for index, hour in enumerate(period.hours):
            writer.writerow(
                [
                    hour,
                    *[
                        ""
                        if (value := period.values[item][index]) is None
                        else f"{value * energy_unit(item.bus)[1]:.3f}"
                        for item in series
                    ],
                ]
            )


def chart_groups(
    periods: list[Period], series: list[Series]
) -> dict[str, dict[str, list[Series]]]:
    """Per panel, the series drawn individually; the rest of the panel is drawn summed as 'other'."""

    def energy(item: Series) -> float:
        return sum(
            abs(value)
            for period in periods
            for value in period.values[item]
            if value is not None
        )

    def ranked(items: list[Series]) -> dict[str, list[Series]]:
        ordered = sorted(items, key=energy, reverse=True)
        return {
            "top": ordered[:TOP_SERIES_PER_CHART],
            "other": ordered[TOP_SERIES_PER_CHART:],
        }

    panels = {
        f"{bus} {side}": [
            item for item in series if item.bus == bus and item.role == role
        ]
        for bus in BUSES
        for side, role in (("consumers", "consumer"), ("suppliers", "source"))
    }
    switches = [item for item in series if item.role == "flow"]
    return {
        **{panel: ranked(items) for panel, items in panels.items() if items},
        SWITCH_PANEL: {"top": switches, "other": []},
    }


def chart_lines(
    period: Period, chart: str, group: dict[str, list[Series]]
) -> dict[str, list[float | None]]:
    scale = energy_unit(chart.split(" ")[0])[1]
    other = [
        scale * sum(period.values[item][index] or 0 for item in group["other"])
        for index in range(len(period.hours))
    ]
    return {
        **{
            (
                item.label if not item.direction else f"{item.label} ({item.direction})"
            ): [
                None if value is None else value * scale
                for value in period.values[item]
            ]
            for item in group["top"]
        },
        **(
            {f"other ({len(group['other'])} devices)": other}
            if group["other"] and any(other)
            else {}
        ),
    }


def write_png(
    path: Path, title: str, period: Period, lines: dict[str, list[float | None]]
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(figsize=(13, 6))
    axes.set_prop_cycle(color=plt.get_cmap("tab20").colors)
    positions = list(range(len(period.hours)))
    for label, values in lines.items():
        points = [float("nan") if value is None else value for value in values]
        axes.step(
            [*positions, len(positions)],
            [*points, points[-1]],
            where="post",
            label=label,
            linewidth=1.2,
        )
    ticks = positions[::3] if len(positions) > 24 else positions[::2]
    axes.set_xticks(
        ticks,
        [
            period.hours[index][5:16].replace("T", " ")
            if len(period.hours) > 24
            else period.hours[index]
            for index in ticks
        ],
        rotation=45,
        ha="right",
        fontsize=8,
    )
    axes.set_ylabel(f"{energy_unit(title.split(' ')[0])[0]} per hour")
    axes.set_title(f"{CHART_TITLES[title]} — {period.label}")
    axes.grid(alpha=0.3)
    axes.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1))
    figure.tight_layout()
    figure.savefig(path, dpi=130)
    plt.close(figure)


def missing_devices(series: list[Series], periods: list[Period]) -> list[str]:
    no_data = [
        item
        for item in series
        if all(value is None for period in periods for value in period.values[item])
    ]
    partly = [
        (
            item,
            [
                period.label
                for period in periods
                if all(value is None for value in period.values[item])
            ],
        )
        for item in series
        if item not in no_data
    ]
    points = [
        "400V | 10P3 panel circuits: no power tags published; only the 10P3 feeder (10P0-3 336Q01) is measured.",
        "350V | outgoing lines (DCOPP breakers 02-71-u10x, 02-72-u10x): readings absent 31 Oct–11 Nov, 0 V / 0 W from 12 Nov; 350V consumers cannot be broken down.",
        "400V | heat recovery pump compression chiller - 10P0-1 156Q01: reads a constant −28 W, kept as published.",
        "350V | epic fwd-2 - 02-72-t102: reads 0 on the 700V side but a constant 0.04 kW from 350V on the 350V side, kept as published.",
        "350V | epic aft-2 - 02-71-t102: returns power from 350V to 700V in every hour (e.g. 41.6 kWh on 7–8 Nov) while epic aft-1 feeds 350V: likely power circulating between the two aft converters, not 350V load.",
        "24V: not all 24V consumption is measured. Many outgoing groups have no Leuze module; on 14E1 about 36 A of the 61 A from the power supplies passes no Leuze module (7–8 Nov).",
        "24V: most Leuze modules on 14E2 and 14E3 read 0 mA, also where the module is switched on (e.g. AIS 14e2-60f01, autopilot 14e2-61f01, gyrocompass 2 14e2-63f01), while the 14E2 power supplies deliver about 32 A.",
        *sorted(
            {
                f"{item.bus} | {item.label}: no data in any weekend; {history_note(series_by_label(series, item.bus, item.label))}."
                for item in no_data
            }
        ),
        *sorted(
            {
                f"{item.bus} | {item.label}: no data on {', '.join(labels)}."
                for item, labels in partly
                if labels
            }
        ),
        *sorted(
            {
                f"{bus} | {label}: reads 0 in all three weekends; {history_note(series_by_label(series, bus, label))}."
                for (bus, label), energy in device_energy(
                    series, periods, no_data
                ).items()
                if energy == 0
            }
        ),
    ]
    return sorted(
        points, key=lambda point: BUSES.index(point.split(" ")[0].rstrip(":"))
    )


def series_by_label(series: list[Series], bus: str, label: str) -> list[Series]:
    return [item for item in series if item.bus == bus and item.label == label]


def history_sources(item: Series) -> list[tuple[str, str, str]]:
    kind, _, ident = item.key.partition(":")
    epic_tables = {
        "02-71-t101": "350v_conv_aft_1",
        "02-71-t102": "350v_conv_aft_2",
        "02-72-t101": "350v_conv_fwd_1",
        "02-72-t102": "350v_conv_fwd_2",
    }
    sources = {
        "powertag": [("power_tags", f"topic = '{ident}'", "active_power_total")],
        "leuze": [
            (
                "marpower__450000_24vdc_system",
                f"topic = 'marpower/450000-24vdc-system/{ident}'",
                "output_current__value",
            )
        ],
        "weidmuller": [
            (
                "marpower__450000_24vdc_system",
                f"topic = 'marpower/450000-24vdc-system/conv/{ident}'",
                "power__value",
            )
        ],
        "brightloop-in": [
            (
                "marpower__450000_main_power_storage_errors",
                f"topic = 'marpower/450000-main-power-storage-errors/{ident[1:]}'",
                "pv_power__value",
            )
        ],
        "shore": [
            (
                "marpower__450000_dc_distribution_esi",
                f"topic = 'marpower/450000-dc-distribution-esi/{ident}'",
                "esi_ac_bus_active_power_3_phase__value",
            )
        ],
        "epic-in": [
            (
                "marpower__busbar",
                f"topic = 'marpower/busbar/epc-{ident[3:]}'",
                "hvdc_power__value",
            ),
            (
                f"marpower__450000_dc_distribution__{epic_tables.get(ident, '')}",
                "true",
                "hvdc_power__value",
            ),
        ],
    }
    same_device = {"brightloop-out": "brightloop-in", "epic-out": "epic-in"}
    return sources.get(same_device.get(kind, kind), [])


def history_note(items: list[Series]) -> str:
    sources = [source for item in items for source in history_sources(item)]
    rows = [
        row
        for table, condition, column in sources
        for row in query(
            f"SELECT min(timestamp), max(timestamp), max(CASE WHEN abs({column}) > 1 THEN timestamp END) FROM {table} WHERE {condition}"
        )
    ]
    first = [row[0] for row in rows if row[0] is not None]
    last_nonzero = [row[2] for row in rows if row[2] is not None]
    if not first:
        return "never published"
    if last_nonzero:
        return f"last reading above 0 on {history_date(max(last_nonzero))}"
    return f"has read 0 ever since it started publishing on {history_date(min(first))}"


def history_date(timestamp: int) -> str:
    seconds = timestamp / 1e9 if timestamp > 1e14 else timestamp / 1e3
    moment = datetime.fromtimestamp(seconds, tz=UTC)
    return f"{moment.day} {moment:%b %Y}"


def device_energy(
    series: list[Series], periods: list[Period], excluded: list[Series]
) -> dict[tuple[str, str], float]:
    energy: dict[tuple[str, str], float] = defaultdict(float)
    for item in series:
        if item not in excluded:
            energy[(item.bus, item.label)] += sum(
                abs(value)
                for period in periods
                for value in period.values[item]
                if value is not None
            )
    return energy


def anomaly_notes(
    weekends: list[Weekend], periods: list[Period], series: list[Series]
) -> list[str]:
    def propulsion_hours(weekend: Weekend) -> int:
        rows = query(
            f"SELECT {hour_bin()}, max(consumed_power__value) FROM marpower__150000_propulsion_ara WHERE {weekend.sql_filter()} GROUP BY 1 HAVING max(consumed_power__value) > 10"
        )
        return len(rows)

    shore = [item for item in series if item.key.startswith("shore:")]
    galley = [
        item
        for item in series
        if item.key.startswith("powertag:") and item.technical_name.startswith("10P2 ")
    ]

    def notes(weekend: Weekend, period: Period) -> list[str]:
        shore_off = [
            index
            for index in range(48)
            if sum(period.values[item][index] or 0 for item in shore) < 0.1
        ]
        galley_peak = max(
            range(48),
            key=lambda index: sum(period.values[item][index] or 0 for item in galley),
        )
        galley_kwh = sum(period.values[item][galley_peak] or 0 for item in galley)
        return [
            f"{period.label}: propulsion drives active in {propulsion_hours(weekend)} of 48 hours.",
            f"{period.label}: shore power below 0.1 kWh in {len(shore_off)} of 48 hours"
            + (f" ({hour_ranges(period, shore_off)})." if shore_off else "."),
            f"{period.label}: galley panel 10P2 peak {galley_kwh:.1f} kWh in the hour from {short_time(period.hours[galley_peak])}.",
        ]

    return [
        note
        for weekend, period in zip(weekends, periods)
        for note in notes(weekend, period)
    ]


def hour_ranges(period: Period, indices: list[int]) -> str:
    starts = [index for index in indices if index - 1 not in indices]
    ends = [index for index in indices if index + 1 not in indices]
    return ", ".join(
        f"{short_time(period.hours[start])} to {short_time(period.hours[end], 1)}"
        for start, end in zip(starts, ends)
    )


def short_time(iso: str, hours_later: int = 0) -> str:
    moment = datetime.fromisoformat(iso) + timedelta(hours=hours_later)
    return f"{moment:%a %H:%M}"


def balance_lines(weekend_periods: list[Period], series: list[Series]) -> list[str]:
    def energy(period: Period, keys: tuple[str, ...]) -> float:
        return sum(
            total(period.values[item]) for item in series if item.key.startswith(keys)
        )

    def lines(period: Period) -> list[str]:
        sources_700 = energy(period, ("shore:", "brightloop-out:", "epic-out:"))
        consumers_700 = energy(period, ("inverter:", "brightloop-in:", "epic-in:"))
        meters_400 = energy(period, ("acmeter:",))
        tags_400 = energy(period, ("powertag:",))
        supplies_24 = energy(period, ("weidmuller:",))
        leuze_24 = energy(period, ("leuze:",))
        return [
            f"{period.label}, 700V: sources {sources_700:.0f} kWh, consumers {consumers_700:.0f} kWh, difference {sources_700 - consumers_700:.0f} kWh ({(sources_700 - consumers_700) / 48:.1f} kW mean).",
            f"{period.label}, 400V: uGrid AC meters {meters_400:.0f} kWh, power tags {tags_400:.0f} kWh, difference {meters_400 - tags_400:.0f} kWh ({(meters_400 - tags_400) / 48:.1f} kW mean).",
            f"{period.label}, 24V: power supplies {supplies_24:.0f} kWh, Leuze modules {leuze_24:.0f} kWh, difference {supplies_24 - leuze_24:.0f} kWh ({(supplies_24 - leuze_24) / 48:.1f} kW mean).",
        ]

    return [line for period in weekend_periods for line in lines(period)]


def device_rows(series: list[Series]) -> list[tuple[str, str, str, str]]:
    return sorted(
        {
            (item.bus, item.name or "–", item.technical_name, item.source)
            for item in series
        }
    )


METHOD = [
    "Source: GreptimeDB on board Zero (raw MQTT messages), tables from before the 450000 topic change of 17 Nov 2026. Device names and technical names follow the 450000 device metadata.",
    "Each value is the mean of all power samples in the hour, in kW (W for 24 V), which equals the energy in kWh (Wh for 24 V) for that hour. Times are ship time (CET, UTC+1); a weekend runs Saturday 00:00 to Monday 00:00.",
    "Average: for each hour of the day, the mean over the six days of the three weekends.",
    "uGrid inverters (05-11-u101, 05-12-u101), Brightloops and shore converters publish kW; multiplied by 1000 to W.",
    "Brightloops: pv_power has no sign. Each sample counts as 'to battery' while that pack's charging flag is set, and as 'from battery' otherwise.",
    "Epic converters, 700 V side: hvdc_power in W (hvdc_voltage × hvdc_current matches hvdc_power). Positive samples count as 'to 350V', negative as 'from 350V'. Until 5 Nov the converters published on marpower/busbar/epc-*, after that on the 450000 tables; both are used.",
    "DC switches: P = DcvS0 × DccS0, with DccS0 taken as A (the IO list gives no scale). These are flows along the 700 V bus, not consumption. Positive and negative current are split per sample. On 5 Nov, with the aft thrusters running, 05-72 went positive and 05-74 negative in step with thruster power: the sign shows the direction of flow along the bus.",
    "400 V: power tags, W. Feeders 10P0-1 135Q01 (to 10P1) and 10P0-3 335Q01 (to 10P2) are left out because the 10P1 and 10P2 circuits are measured individually. 10P0-3 336Q01 (to 10P3) is kept as the only measurement of 10P3.",
    "400 V supply: uGrid AC meters 10P0-1 100Q01 and 10P0-3 300Q01, total active power measured on the 400 V AC side of each uGrid.",
    "24 V supply: Weidmuller power supplies, power measured at their 24 V output (about 27–28 V).",
    "Suppliers are drawn below zero in the charts; that sign is a chart convention, not the measured sign. The CSV files give all values as positive energy with the direction in the column name.",
    "24 V: Leuze modules publish output current in mA; power = current / 1000 × the hourly mean output voltage of the bus's power supplies (14E1 supplies for 14E1; 14E2 supplies for 14E2 and 14E3).",
    "350 V: Epic converter output, lvdc_voltage × lvdc_current (W), per converter.",
    "Propulsion drives and solar converters are not included.",
]


def write_html(
    path: Path,
    periods: list[Period],
    groups: dict[str, dict[str, list[Series]]],
    series: list[Series],
    missing: list[str],
    anomalies: list[str],
    balance: list[str],
) -> None:
    from html import escape

    import plotly.offline

    data = {
        period.slug: {
            "label": period.label,
            "hours": period.hours,
            "charts": {
                chart: chart_lines(period, chart, group)
                for chart, group in groups.items()
            },
        }
        for period in periods
    }
    charts = [
        *[
            {
                "title": BUS_TITLES[bus],
                "unit": energy_unit(bus)[0],
                "bars": [
                    panel
                    for panel in (f"{bus} consumers", f"{bus} suppliers")
                    if panel in groups
                ],
            }
            for bus in BUSES
        ],
        {"title": CHART_TITLES[SWITCH_PANEL], "unit": "kWh", "lines": SWITCH_PANEL},
    ]
    devices = "".join(
        f"<tr><td>{escape(bus)}</td><td>{escape(name)}</td><td>{escape(technical)}</td><td>{escape(source)}</td></tr>"
        for bus, name, technical, source in device_rows(series)
    )
    period_buttons = "".join(
        f'<button data-period="{period.slug}">{escape(period.label)}</button>'
        for period in periods
    )
    sections = "".join(
        f'<h2>{escape(chart["title"])}</h2><div class="chart" id="chart-{index}"></div>'
        for index, chart in enumerate(charts)
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Zero hotel load</title>
<style>
body {{ background: #fff; color: #000; font: 14px/1.45 -apple-system, "Helvetica Neue", Arial, sans-serif; margin: 0 auto; max-width: 1200px; padding: 16px; }}
h1 {{ font-size: 20px; margin: 0 0 4px; }} h2 {{ font-size: 15px; margin: 28px 0 4px; border-top: 1px solid #000; padding-top: 8px; }}
.controls {{ position: sticky; top: 0; background: #fff; padding: 8px 0; border-bottom: 1px solid #000; z-index: 1; display: flex; flex-wrap: wrap; gap: 4px 16px; }}
.group {{ display: flex; flex-wrap: wrap; gap: 4px; }}
button {{ font: inherit; background: #fff; color: #000; border: 1px solid #000; padding: 3px 10px; cursor: pointer; }}
button.active {{ background: #000; color: #fff; }} button:disabled {{ opacity: .35; cursor: default; }}
.chart {{ height: 520px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 12px; }} td, th {{ border: 1px solid #000; padding: 2px 6px; text-align: left; vertical-align: top; }}
ul {{ padding-left: 18px; }} .note {{ font-size: 12px; }}
</style></head><body>
<h1>S/Y Zero — electrical energy per consumer, weekends Oct–Nov 2026</h1>
<p class="note">Hourly energy per device (kWh; 24 V in Wh) on the 700 V, 400 V, 350 V and 24 V buses. Consumers are stacked above zero, suppliers below zero. Each side shows its {TOP_SERIES_PER_CHART} largest devices; the rest are summed as "other". All devices are in the CSV files.</p>
<div class="controls"><div class="group">{period_buttons}</div><div class="group" id="days"><button data-day="both">Sat + Sun</button><button data-day="sat">Saturday</button><button data-day="sun">Sunday</button></div></div>
{sections}
<h2>Calculations and corrections</h2><ul>{"".join(f"<li>{escape(item)}</li>" for item in METHOD)}</ul>
<h2>Missing devices and open points</h2><ul>{"".join(f"<li>{escape(item)}</li>" for item in missing)}</ul>
<h2>Balance per weekend</h2><ul>{"".join(f"<li>{escape(item)}</li>" for item in balance)}</ul>
<h2>Notes per weekend</h2><ul>{"".join(f"<li>{escape(item)}</li>" for item in anomalies)}</ul>
<h2>Devices</h2><table><tr><th>Bus</th><th>Name</th><th>Technical name</th><th>Signal</th></tr>{devices}</table>
<script>{plotly.offline.get_plotlyjs()}</script>
<script>
const DATA = {json.dumps(data)};
const CHARTS = {json.dumps(charts)};
const state = {{ period: "{periods[0].slug}", day: "both" }};
function render() {{
  const period = DATA[state.period];
  const isAverage = state.period === "average";
  const range = isAverage || state.day === "both" ? [0, period.hours.length] : state.day === "sat" ? [0, 24] : [24, 48];
  const hours = period.hours.slice(...range);
  CHARTS.forEach((chart, index) => {{
    const lines = chart.lines !== undefined;
    const traces = lines
      ? Object.entries(period.charts[chart.lines]).map(([name, values]) => ({{
          x: hours, y: values.slice(...range), name, type: "scatter", mode: "lines", line: {{ shape: "hv", width: 1.5 }},
          hovertemplate: `%{{y:.2f}} ${{chart.unit}}<extra>%{{fullData.name}}</extra>`,
        }}))
      : chart.bars.flatMap(panel => {{
          const sign = panel.endsWith("suppliers") ? -1 : 1;
          return Object.entries(period.charts[panel]).map(([name, values]) => ({{
            x: hours, y: values.slice(...range).map(value => value === null ? null : sign * value), name: sign < 0 && !name.endsWith(")") ? `${{name}} (supply)` : name,
            type: "bar", legendgroup: panel, hovertemplate: `%{{fullData.name}}<br>%{{x}}<br>%{{y:.2f}} ${{chart.unit}}<extra></extra>`,
          }}));
        }});
    Plotly.react(`chart-${{index}}`, traces, {{
      barmode: "relative", bargap: 0.05,
      margin: {{ l: 56, r: 8, t: 8, b: 48 }}, hovermode: lines ? "x unified" : "closest", paper_bgcolor: "#fff", plot_bgcolor: "#fff",
      yaxis: {{ title: lines ? `${{chart.unit}} per hour` : `${{chart.unit}} per hour (consumers up, suppliers down)`, gridcolor: "#ddd", zerolinecolor: "#000" }},
      xaxis: {{ gridcolor: "#eee", type: isAverage ? "category" : "date" }},
      legend: {{ font: {{ size: 10 }} }}, font: {{ color: "#000" }},
    }}, {{ displaylogo: false, responsive: true }});
  }});
  document.querySelectorAll("[data-period]").forEach(b => b.classList.toggle("active", b.dataset.period === state.period));
  document.querySelectorAll("[data-day]").forEach(b => {{ b.classList.toggle("active", !isAverage && b.dataset.day === state.day); b.disabled = isAverage; }});
}}
document.querySelectorAll("[data-period]").forEach(b => b.addEventListener("click", () => {{ state.period = b.dataset.period; render(); }}));
document.querySelectorAll("[data-day]").forEach(b => b.addEventListener("click", () => {{ state.day = b.dataset.day; render(); }}));
render();
</script></body></html>"""
    path.write_text(html)


def main() -> None:
    names = load_names()
    tag_rows = power_tag_rows()
    weekends = [Weekend(saturday=saturday) for saturday in SATURDAYS]
    collected = [collect(weekend, names, tag_rows) for weekend in weekends]
    all_series = list(dict.fromkeys(item for kwh in collected for item in kwh))
    weekend_periods = [
        weekend_period(weekend, kwh, all_series)
        for weekend, kwh in zip(weekends, collected)
    ]
    missing = missing_devices(all_series, weekend_periods)
    series = [
        item
        for item in all_series
        if any(
            value is not None
            for period in weekend_periods
            for value in period.values[item]
        )
    ]
    periods = [*weekend_periods, average_period(weekend_periods, series)]
    groups = chart_groups(weekend_periods, series)
    anomalies = anomaly_notes(weekends, weekend_periods, series)

    OUT.mkdir(exist_ok=True)
    (OUT / "png").mkdir(exist_ok=True)
    for stale in (OUT / "png").glob("*.png"):
        stale.unlink()
    csv_paths = [OUT / f"{period.slug}.csv" for period in weekend_periods]
    for path, period in zip(csv_paths, weekend_periods):
        write_csv(path, period, series)
    png_paths = [
        OUT / "png" / f"{chart.replace(' ', '-')}_{period.slug}.png"
        for period in periods
        for chart in groups
    ]
    for path, (period, chart) in zip(
        png_paths, [(period, chart) for period in periods for chart in groups]
    ):
        write_png(path, chart, period, chart_lines(period, chart, groups[chart]))
    html_path = OUT / "report.html"
    write_html(
        html_path,
        periods,
        groups,
        series,
        missing,
        anomalies,
        balance_lines(weekend_periods, series),
    )

    zip_path = OUT / "zero-hotel-load-2026-11.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in [*csv_paths, *png_paths, html_path]:
            archive.write(path, path.relative_to(OUT))
    print(zip_path)


if __name__ == "__main__":
    main()
