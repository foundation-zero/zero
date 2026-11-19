# zero-alert-forwarder

Forwards alerts of the AMCS to [ntfy](https://ntfy.sh), so the crew gets them on their phones.
Alarms raised in the technical space do not sound above decks otherwise. It also publishes the
current alarms on MQTT, which zero-mqtt-graphql serves to the Alarms app of zero-ui.

## Overview

The AMCS stores its alerts in the `alerts` MySQL database, in one table per UTC day named
`YYYY/MM/DD`. Every state change of an alarm is a row of its own (`Activated`, `Acknowledged`,
`Idle`, ...). MySQL cannot notify on new rows, so the service polls the day tables every few
seconds and sends each new alert that passes the filters to ntfy.

- The database is only ever read; sessions are opened `READ ONLY`.
- On startup the existing alerts of the day are skipped, only alerts raised afterwards are forwarded.
- A failed poll is retried at the next interval, a failed notification `--attempts` times.

### Reminders

An alarm that nobody acknowledges is notified again, with growing urgency: 20 seconds after
the alert, then after 10, 5 and 3 more seconds, and every second from then on. Only an `Acknowledged`
update of the same alarm (matched on system, tag and location) stops the reminders; an alarm
that went `Idle` unacknowledged keeps pinging, and a new `Activated` restarts the progression. Reminders reuse the alert's sequence ID, so they update the notification
instead of stacking. They are kept in memory, so a restart forgets them. Set
`--reminder-delays-seconds '[]'` to turn them off.

### Mirrored databases

With several `--mysql-hosts` the service treats them as mirrors of one database, which
requires identical alert ids on every host. They share a single cursor and take turns: with
two hosts and a 10 second interval, a poll happens every 5 seconds, alternating between the hosts.
Each alert is forwarded once, an alert shows up as soon as either host has it, and a host
that is down only costs its own turns.

### Rolling releases

Every notification carries a sequence ID built from the alert's UTC day and id, which is the
same on every pod and mirror. During a rolling release both pods may see an alert raised in
the overlap; ntfy treats the second publish as an update of the first notification rather than
a new one. The server still stores both messages, so only the apps collapse them.

### Liveness and readiness

With `--liveness-path` the file is touched after every poll, successful or not, and after
every forwarded alert, so a large batch does not look like a hung loop. The Helm chart's
liveness probe restarts the container when the file is older than `livenessMaxAgeSeconds`.
That value must exceed one notification's retries, `attempts * 10s + (attempts - 1) * interval`,
and `--poll-timeout-seconds`, which bounds a poll of a single mirror so a stalled database
cannot block the other one. With an alarm list, it must also exceed `--history-timeout-seconds`,
which bounds the first poll instead.

With `--readiness-path` the file is created once the starting point of the polling is known.
The chart's readiness probe makes a rolling update wait for that, since alerts raised before
it would be skipped as history.

### Priorities

| AMCS priority | ntfy priority |
|---|---|
| `GEA`, `Emergency`, `Alarm` | 5 (max) |
| `Warning`, unknown | 4 (high) |
| `Caution` | 3 (default) |
| `Event` | 1 (min) |

By default only `Activated` alerts of `Warning` and up are forwarded: `Caution` is dominated by
flapping "service is not healthy" notices, and the other updates (`Idle`, `Acknowledged`, ...)
only follow an alarm that was already forwarded.

### Alarm list

With `--mqtt-host` the service also keeps a list of alarms and publishes it to
`alerts/alarm-list` every `--alarm-list-interval-seconds`. An alarm is identified by its system,
tag and location, like the reminders, and is folded from every row of `--alarm-list-min-priority`
and up, whatever `--updates` forwards to ntfy:

| Update | Active | Acknowledged |
|---|---|---|
| `Activated` | yes | no |
| `Acknowledged` | unchanged (no, for an alarm not seen before) | yes |
| `Idle` | no | unchanged |
| others | unchanged | unchanged, and only for an alarm already listed |

The list holds every active alarm, and every alarm that is no longer active but changed within
`--alarm-list-window-minutes`. The AsyncAPI spec of the topic
(`python -m zero_alert_forwarder print-asyncapi`, collected by `scripts/aggregate-specs.sh`) gives it a
TTL of 30 seconds, so zero-mqtt-graphql stops serving it soon after the forwarder stops. For the
same reason it is not retained.

At startup the list is rebuilt from all of today's alerts, and from yesterday's when the window
reaches into it, without notifying anyone. An alarm that has been active since before then
appears only when it changes again. Reading that history can take longer than a regular poll,
so the first poll is bounded by `--history-timeout-seconds` instead of `--poll-timeout-seconds`.

### Extending

Alerts come from an `AlertSource` and go to a `Notifier` (see `source.py` and `ntfy.py`).
Alerts over MQTT are expected to become a second `AlertSource`; a self-hosted ntfy only
needs `--ntfy-url`.

## Configuration

Settings are read from CLI flags of the `run` subcommand, environment variables or a `.env` file.
Without a subcommand, as in the container, the service runs with the settings of the
environment.

| Option | Environment | Default |
|---|---|---|
| `--mysql-hosts` | `MYSQL_HOSTS` | required, JSON list |
| `--mysql-port` | `MYSQL_PORT` | `3306` |
| `--mysql-user` | `MYSQL_USER` | required |
| `--mysql-password` | `MYSQL_PASSWORD` | required |
| `--mysql-database` | `MYSQL_DATABASE` | `alerts` |
| `--ntfy-url` | `NTFY_URL` | `https://ntfy.sh` |
| `--ntfy-topic` | `NTFY_TOPIC` | required |
| `--ntfy-token` | `NTFY_TOKEN` | none |
| `--poll-interval-seconds` | `POLL_INTERVAL_SECONDS` | `10` (1 - 60) |
| `--min-priority` | `MIN_PRIORITY` | `Warning` |
| `--updates` | `UPDATES` | `["Activated"]` |
| `--attempts` | `ATTEMPTS` | `3` |
| `--reminder-delays-seconds` | `REMINDER_DELAYS_SECONDS` | `[20, 10, 5, 3, 1]`, last repeats |
| `--dry-run` | `DRY_RUN` | `false` |
| `--poll-timeout-seconds` | `POLL_TIMEOUT_SECONDS` | `10` |
| `--history-timeout-seconds` | `HISTORY_TIMEOUT_SECONDS` | `60` |
| `--liveness-path` | `LIVENESS_PATH` | none |
| `--readiness-path` | `READINESS_PATH` | none |
| `--mqtt-host` | `MQTT_HOST` | none, publishes no alarm list |
| `--mqtt-port` | `MQTT_PORT` | `1883` |
| `--mqtt-username` | `MQTT_USERNAME` | none |
| `--mqtt-password` | `MQTT_PASSWORD` | none |
| `--alarm-list-min-priority` | `ALARM_LIST_MIN_PRIORITY` | `Warning` |
| `--alarm-list-window-minutes` | `ALARM_LIST_WINDOW_MINUTES` | `60` |
| `--alarm-list-interval-seconds` | `ALARM_LIST_INTERVAL_SECONDS` | `5` (1 - 10) |

ntfy topics on ntfy.sh are public to anyone who knows the name, so pick a long random one.

## Usage

```bash
uv run python -m zero_alert_forwarder run \
  --mysql-hosts '["localhost"]' --mysql-user chameleon --mysql-password chameleon \
  --ntfy-topic <topic>
```

Add `--dry-run` to log what would be sent instead of notifying anyone.

## Development

```bash
uv sync --locked
uv run pytest
uv run ruff check
uv run pyright
```

The tests need neither a database, a broker nor network access.
