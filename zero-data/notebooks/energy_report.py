import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    from datetime import datetime, timedelta

    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from sqlalchemy import create_engine, text

    return create_engine, datetime, mo, os, pd, px, text, timedelta


@app.cell
def _(mo):
    mo.md(
        """
        # Domestic energy report

        Weekly electrical consumption built from the dbt view
        `views.slv_power_tags`, which joins GreptimeDB's `public.power_tags`
        with `public.power_tag_metadata` (`main_group` / `sub_group`).

        Energy is the integral of `active_power_total` over the reporting window:
        each topic is averaged into 1-minute buckets, then summed
        (`sum(avg_W) / 60 / 1000` → kWh). Distribution-panel feed meters are
        excluded, as they measure the sum of their downstream tags. Pick a
        Sunday-to-Sunday week below; the controls default to the most recent
        complete week in the data.
        """
    )
    return


@app.cell
def _(create_engine, os):
    GREPTIME_MYSQL_URL = os.environ.get(
        "GREPTIME_MYSQL_URL",
        "mysql+pymysql://app@greptime-zero.tail0b4840.ts.net:4002/public",
    )
    engine = create_engine(GREPTIME_MYSQL_URL, pool_pre_ping=True)
    return (engine,)


@app.cell
def _(engine, pd, text, timedelta):
    with engine.connect() as _conn:
        _latest = _conn.execute(text("SELECT MAX(timestamp) FROM power_tags")).scalar()
    latest_ts = pd.Timestamp(_latest)
    # Most recent Sunday on or before the newest sample.
    last_sunday = latest_ts.date() - timedelta(days=(latest_ts.weekday() + 1) % 7)
    default_start = last_sunday - timedelta(days=7)
    default_end = last_sunday
    return default_end, default_start, latest_ts


@app.cell
def _(default_end, default_start, mo, timedelta):
    week = mo.ui.date_range(
        start=default_start - timedelta(days=90),
        stop=default_end + timedelta(days=7),
        value=(default_start, default_end),
        label="Reporting week (Sunday → Sunday)",
    )
    group_by = mo.ui.dropdown(
        options={
            "Main group": "main_group",
            "Sub group": "sub_group",
            "Panel": "panel",
            "Consumer": "consumer",
        },
        value="Main group",
        label="Group by",
    )
    resolution = mo.ui.dropdown(
        options={
            "5 min": "5 minutes",
            "15 min": "15 minutes",
            "30 min": "30 minutes",
            "1 hour": "1 hour",
        },
        value="15 min",
        label="Power resolution",
    )
    mo.hstack([week, group_by, resolution], justify="start", gap=2)
    return group_by, resolution, week


@app.cell
def _(datetime, engine, mo, pd, text):
    RESOLUTION_OPTIONS = {"5 minutes", "15 minutes", "30 minutes", "1 hour"}

    # Distribution-panel feed meters measure the sum of their downstream tags, so
    # counting them alongside those tags double-counts the same energy.
    EXCLUDE_DISTRIBUTION_PANELS = "AND UPPER(COALESCE(consumer, '')) NOT LIKE '%DISTR%'"

    @mo.cache
    def load_energy_per_topic(start: datetime, end: datetime) -> pd.DataFrame:
        query = text(
            f"""
            SELECT x.topic,
                   MAX(x.consumer) AS consumer,
                   MAX(x.panel) AS panel,
                   SUM(x.minute_avg_power_w) / 60.0 / 1000.0 AS energy_kwh,
                   MAX(x.main_group) AS main_group,
                   MAX(x.sub_group) AS sub_group
            FROM (
                SELECT date_bin('1 minute'::INTERVAL, ts) AS minute,
                       topic,
                       AVG(active_power_total) AS minute_avg_power_w,
                       MAX(consumer) AS consumer,
                       MAX(panel) AS panel,
                       MAX(main_group) AS main_group,
                       MAX(sub_group) AS sub_group
                FROM views.slv_power_tags
                WHERE ts >= :start AND ts < :end
                      {EXCLUDE_DISTRIBUTION_PANELS}
                GROUP BY minute, topic
            ) AS x
            GROUP BY x.topic
            """
        )
        with engine.connect() as conn:
            return pd.read_sql(query, conn, params={"start": start, "end": end})

    @mo.cache
    def load_energy_per_day(start: datetime, end: datetime) -> pd.DataFrame:
        query = text(
            f"""
            SELECT date_trunc('day', x.minute) AS day,
                   x.topic,
                   SUM(x.minute_avg_power_w) / 60.0 / 1000.0 AS energy_kwh,
                   MAX(x.main_group) AS main_group,
                   MAX(x.sub_group) AS sub_group,
                   MAX(x.panel) AS panel,
                   MAX(x.consumer) AS consumer
            FROM (
                SELECT date_bin('1 minute'::INTERVAL, ts) AS minute,
                       topic,
                       AVG(active_power_total) AS minute_avg_power_w,
                       MAX(main_group) AS main_group,
                       MAX(sub_group) AS sub_group,
                       MAX(panel) AS panel,
                       MAX(consumer) AS consumer
                FROM views.slv_power_tags
                WHERE ts >= :start AND ts < :end
                      {EXCLUDE_DISTRIBUTION_PANELS}
                GROUP BY minute, topic
            ) AS x
            GROUP BY day, x.topic
            """
        )
        with engine.connect() as conn:
            return pd.read_sql(query, conn, params={"start": start, "end": end})

    @mo.cache
    def load_power_timeseries(
        start: datetime, end: datetime, interval: str
    ) -> pd.DataFrame:
        if interval not in RESOLUTION_OPTIONS:
            raise ValueError(f"Unsupported resolution: {interval}")
        query = text(
            f"""
            SELECT date_bin('{interval}'::INTERVAL, ts) AS time,
                   topic,
                   AVG(active_power_total) AS avg_power_w,
                   MAX(main_group) AS main_group,
                   MAX(sub_group) AS sub_group,
                   MAX(panel) AS panel,
                   MAX(consumer) AS consumer
            FROM views.slv_power_tags
            WHERE ts >= :start AND ts < :end
                  {EXCLUDE_DISTRIBUTION_PANELS}
            GROUP BY time, topic
            """
        )
        with engine.connect() as conn:
            return pd.read_sql(query, conn, params={"start": start, "end": end})

    return load_energy_per_day, load_energy_per_topic, load_power_timeseries


@app.cell
def _(mo, pd):
    UNCLASSIFIED = "Unclassified"

    def classify(frame: pd.DataFrame, group_col: str) -> pd.DataFrame:
        groups = frame[group_col].fillna(UNCLASSIFIED).replace("", UNCLASSIFIED)
        return frame.assign(group=groups)

    return classify, UNCLASSIFIED


@app.cell
def _(datetime, mo, week):
    start_dt = datetime.combine(week.value[0], datetime.min.time())
    end_dt = datetime.combine(week.value[1], datetime.min.time())
    mo.stop(
        end_dt <= start_dt,
        mo.md("**Pick a window where the end date is after the start date.**"),
    )
    return end_dt, start_dt


@app.cell
def _(
    end_dt,
    load_energy_per_day,
    load_energy_per_topic,
    load_power_timeseries,
    mo,
    resolution,
    start_dt,
):
    energy = load_energy_per_topic(start_dt, end_dt)
    daily = load_energy_per_day(start_dt, end_dt)
    timeseries = load_power_timeseries(start_dt, end_dt, resolution.value)
    mo.stop(
        energy.empty,
        mo.md("**No power-tag data in the selected window.**"),
    )
    return daily, energy, timeseries


@app.cell
def _(energy, mo, timeseries):
    total_kwh = energy["energy_kwh"].sum()
    total_power = timeseries.groupby("time")["avg_power_w"].sum()
    peak_kw = total_power.max() / 1000
    avg_kw = total_power.mean() / 1000
    mo.hstack(
        [
            mo.stat(f"{total_kwh:,.1f}", label="Consumption (kWh)", bordered=True),
            mo.stat(f"{peak_kw:,.1f}", label="Peak power (kW)", bordered=True),
            mo.stat(f"{avg_kw:,.1f}", label="Average power (kW)", bordered=True),
            mo.stat(
                f"{energy['topic'].nunique():,}", label="Active tags", bordered=True
            ),
        ],
        justify="start",
    )
    return


@app.cell
def _(classify, energy, group_by):
    group_energy = (
        classify(energy, group_by.value)
        .groupby("group", as_index=False)["energy_kwh"]
        .sum()
        .sort_values("energy_kwh", ascending=False)
    )
    return (group_energy,)


@app.cell
def _(classify, daily, group_by):
    daily_by_group = (
        classify(daily, group_by.value)
        .groupby(["day", "group"], as_index=False)["energy_kwh"]
        .sum()
    )
    return (daily_by_group,)


@app.cell
def _(classify, group_by, timeseries):
    group_power = (
        classify(timeseries, group_by.value)
        .groupby(["time", "group"], as_index=False)
        .agg(power_kw=("avg_power_w", lambda power_w: power_w.sum() / 1000))
        .sort_values("time")
    )
    return (group_power,)


@app.cell
def _(energy, group_by, mo, px):
    _top = energy.nlargest(15, "energy_kwh").sort_values("energy_kwh")
    _fig = px.bar(
        _top,
        x="energy_kwh",
        y="consumer",
        orientation="h",
        title=f"Top 15 consumers by energy ({group_by.value})",
        labels={"energy_kwh": "Energy (kWh)", "consumer": ""},
    )
    _fig.update_traces(
        hovertemplate="Consumer: %{y}<br>Energy: %{x:,.1f} kWh<extra></extra>"
    )
    mo.ui.plotly(_fig)
    return


@app.cell
def _(group_by, group_energy, mo, px):
    _fig = px.bar(
        group_energy,
        x="energy_kwh",
        y="group",
        orientation="h",
        title=f"Energy by {group_by.value}",
        labels={"energy_kwh": "Energy (kWh)", "group": ""},
    )
    _fig.update_traces(hovertemplate="%{y}<br>Energy: %{x:,.1f} kWh<extra></extra>")
    _fig.update_layout(yaxis={"categoryorder": "total ascending"})
    mo.ui.plotly(_fig)
    return


@app.cell
def _(daily_by_group, group_by, mo, px):
    _fig = px.bar(
        daily_by_group,
        x="day",
        y="energy_kwh",
        color="group",
        barmode="stack",
        title=f"Daily energy by {group_by.value}",
        labels={"day": "", "energy_kwh": "Energy (kWh)", "group": ""},
    )
    _fig.update_traces(
        hovertemplate="%{x|%a %d %b}<br>%{fullData.name}: %{y:,.1f} kWh<extra></extra>"
    )
    mo.ui.plotly(_fig)
    return


@app.cell
def _(group_by, group_power, mo, px):
    _fig = px.line(
        group_power,
        x="time",
        y="power_kw",
        color="group",
        title=f"Power by {group_by.value}",
        labels={"time": "", "power_kw": "Power (kW)", "group": ""},
    )
    _fig.update_traces(
        hovertemplate="%{x|%a %d %b %H:%M}<br>%{fullData.name}: %{y:,.1f} kW<extra></extra>"
    )
    mo.ui.plotly(_fig)
    return


@app.cell
def _(UNCLASSIFIED, classify, energy, group_by, mo):
    _breakdown = (
        classify(energy, group_by.value)
        .groupby("group", as_index=False)["energy_kwh"]
        .sum()
        .sort_values("energy_kwh", ascending=False)
    )
    _breakdown["share_%"] = (
        _breakdown["energy_kwh"] / _breakdown["energy_kwh"].sum() * 100
    ).round(1)
    _breakdown = _breakdown.rename(columns={"group": group_by.value})
    mo.ui.table(_breakdown, selection=None)
    return


if __name__ == "__main__":
    app.run()
