# Plan: apply ADR 0001 to the zero apps

Temporary: delete this file when the work is done. The rules are in [ADR 0001](../adr/0001-dependency-outages.md); the trigger and outage notes are in [ZERO-2406](https://foundationzero-team.atlassian.net/browse/ZERO-2406).

**Keep it 80/20.** Prefer the simplest change that fixes the actual outage behaviour over full conformance to every rule. Where meeting a rule would mean a large change for little benefit, stop and flag it with the simpler alternative instead of building it.

## Where we are

Three ways the apps break the ADR today:

- **Stuck:** the app stays `Running` without a broker connection until someone restarts it. It loses data silently.
- **Crash:** the app exits when the broker goes away and comes back through `CrashLoopBackOff`. That is safe, but it is red in k9s and adds minutes of restart backoff.
- **Slow:** the app reconnects by itself, but its 60 s backoff cap delays it by up to a minute after the broker is back.

No app reports MQTT connectivity through readiness, and none has the 15 min deadline.

Phase 1 (#971, #974–#977) fixed the reconnects, backoff caps, keepalives and refusals, and gave battery-cells and fiber-optics readiness and the deadline. This section and the table below describe the state before it.

What the logs of the 2026-10-13 RabbitMQ cutover show:

- **RabbitMQ refuses connections with CONNACK 0x87 "Not authorized"** (MQTT 3.1.1 code 5) for 25–65 s after it boots, probably until the topology operator has provisioned the users again. Clients that exit on the first refusal crash-loop through that window.
- **fiber-optics was the only app stuck.** Its MQTT 5 client hung on a socket write (see F3).
- **The F1 apps were not stuck.** power-tags reconnected by itself, late because of the 60 s cap; termodinamica and hull-temperature crash-looped on the refusals. The zmqtt failure in F1 below is real in the library code, but this outage didn't trigger it.

## Flavours

| Flavour | Apps | Today | Main work |
| --- | --- | --- | --- |
| **F1** FastStream/zmqtt through `zero-modbus-bridge` | power-tags, termodinamica, hull-temperature | Slow (power-tags) or crash (others); stuck possible on a refusal during reconnect | Retry refusals and handle give-up once, in the bridge |
| **F2** FastStream/zmqtt, standalone | atpx-nmea | Stuck | Same as F1, plus a second broker and a zmqtt/FastStream upgrade |
| **F3** rumqttc (Rust) | fiber-optics, battery-cells, mqtt-graphql | fiber-optics stuck; the other two reconnect | Readiness and deadline; move fiber-optics to MQTT 3.1.1 |
| **F4** aiomqtt, exits on error | loads-app (api, control), thrs-control (control, simulation, api), domestic-control, data-gen | Crash | Follow-up ticket |
| **F5** third party | vector | Stuck (doesn't re-subscribe) | Existing alert only |

Out of scope: zero-ui (browser client), zero-generator (library, not deployed on its own), alert-forwarder (no MQTT), and sail-systems-mqtt-adapter (separate repo; needs its own ticket).

## Shared pieces

Every flavour needs the same three things. For Python the first two live in the shared `zero-health` package in `packages/py`:

- **Health endpoints:** the app passes in one check per dependency that counts for readiness. A monitor loop runs them every 10 s and keeps the last result. `GET /health/ready` returns 204, or 500 with one line per failing check, e.g. `mqtt: ping failed (not connected)`. `GET /health/alive` always returns 204 from the app's event loop, so it times out only when the loop is blocked, where the deadline cannot fire either. The app logs every change in readiness.
- **Deadline:** after 15 min of continuous not-ready time, the monitor writes the reason to `/dev/termination-log` and exits. The timer resets whenever the app becomes ready. `HEALTH_DEADLINE_SECONDS` changes it per app, but always above 10 min.
- **Probe:** HTTP readiness and liveness probes on port 8080 in each chart.

The probe reads the cached result instead of running the checks. FastStream's `make_ping_asgi` pings the broker on every probe, but we need the monitor loop for the deadline anyway, and some apps have several checks.

For the FastStream apps, a `zero-mqtt` package in `packages/py` builds the broker with the defaults below, wraps it to retry refusals, and provides a check that calls `broker.ping()`.

battery-cells and fiber-optics keep what they already have: a status file the app writes, the same deadline, and an exec readiness probe. Their identical `readiness.rs` moves into one crate in `packages/rust`.

Every flavour also has to meet these:

- **Backoff cap of 30 s.** With zmqtt's and our Rust apps' old 60 s cap, a client could wait a full minute after the broker is back, which misses the "reconnect within about 1 min" target. Done in phase 1.
- **Keepalive of 15 s.** It detects a dead connection; RabbitMQ's keepalive window races the 60 s default. Done in phase 1.
- **Refusals, permanent errors such as bad credentials:** retry a few times, then exit (ADR). This includes 0x87, because RabbitMQ sends it while booting. Done in phase 1: the Python apps exit after about 90 s, the Rust apps after 10 refusals (about 3 min).
- **Required or optional:** each app decides this for each of its dependencies, not only MQTT. MQTT is required for worker pods and optional for pods that serve an HTTP API, so the API stays in its Service and reports values as missing (#905).

Things to know before rolling this out:

- **k9s colours `0/1 Running` the same red as `CrashLoopBackOff`.** Only the STATUS text differs, so a broker outage will still look red. It just won't restart pods.
- **A rollout stalls while a required dependency is down,** because new pods never become ready. It resumes once the dependency is back.

**Decided: the shared code lives in `packages/py` and `packages/rust`,** not copied per app. Apps use the packages as path dependencies; nothing is published. `zero-modbus-bridge` moves into `packages/py` too. There is no shared chart library, so the probe block is copied into each chart.

## F1: power-tags, termodinamica, hull-temperature

Done in #974: `make_broker` sets `max_attempts=None`, the 30 s cap and the 15 s keepalive, exits from `on_connection_recovery_failed`, and wraps the client to retry CONNACK refusals (zmqtt never retries them). All three apps use it. `zero-mqtt` takes it over.

Left for phase 2:
- **Modbus gateways:** optional (logged only) for power-tags, which reads many; required for termodinamica and hull-temperature, which each read one.

Open:
- **zmqtt upstream fix:** merged in zMQTT#129, waiting for a release; ZERO-2532 drops the wrapper.
- **Replay buffer (#716):** the ADR leaves replay out of scope. hull-temperature also publishes a relay command, which should not be replayed after an outage. Does that need its own ticket?

## F2: atpx-nmea

Done in #977: the zmqtt and FastStream upgrade, and the F1 handling for both brokers, through a copy of the bridge's `mqtt.py`.

Left for phase 2:
- **Both brokers:** delete atpx-nmea's copy of `mqtt.py` and use `zero-mqtt` and `zero-health`, one required check per broker.
- **Verification** also covers an outage of the A+T input broker. That broker is outside our control, so simulate it rather than touch it.

Proposed: **the A+T input broker is required.** Without it the pod has nothing to do, so it shows `0/1` whenever A+T's broker is down. That is outside our control, but it is the honest signal.

## F3: fiber-optics, battery-cells, mqtt-graphql

**fiber-optics root cause:** it was our only app on rumqttc's MQTT 5 client, whose event loop writes and flushes the socket without a timeout (`rumqttc v5/eventloop.rs`, 0.24 and 0.25; upstream issue [bytebeamio/rumqtt#1078](https://github.com/bytebeamio/rumqtt/issues/1078)). The MQTT 3.1.1 client wraps the flush in a timeout. In the cutover RabbitMQ's pod IP disappeared without a TCP reset, fiber-optics' send buffer filled with ~16 KB publishes at 10 Hz, and the flush never returned. No error was logged, and the keepalive check never ran. There was no RabbitMQ memory or disk alarm.

Done in phase 1: battery-cells (#971) and fiber-optics (#976, now on the MQTT 3.1.1 client) report readiness through a status file and exit on the deadline. mqtt-graphql (#975) caps its backoff and exits on refusals; its MQTT is optional, so it has no readiness. Left: deduplicating `readiness.rs` in ZERO-2612.

A not-ready fiber-optics or battery-cells pod drops out of its UDP `LoadBalancer` Service, so packets stop reaching it during an outage. We accept that; the packets can't be published anyway.

## F4: loads-app, thrs-control, domestic-control, data-gen

**Decided: a follow-up ticket, [ZERO-2531](https://foundationzero-team.atlassian.net/browse/ZERO-2531).** These apps recover today, just slowly and noisily. aiomqtt has no automatic reconnect: the apps use `async with Client(...)`, and an `MqttError` ends the process. loads-app and thrs-control exit on purpose with `sys.exit(1)` (`loads/api/dependencies.py`, `thrs/graphql/strawberry.py`).

For that ticket:
- **A reconnect loop** around the client, with the 30 s backoff cap and 15 s keepalive. Subscriptions are set up again after each reconnect.
- **Keep thrs-control's heartbeat liveness probe.** It checks the control loop, not MQTT, so it already fits the ADR.
- **Controllers** (thrs-control, domestic-control, loads control): waiting inside the process keeps control state across an outage, and a restart starts from a clean state. Which do we want? Commands queued during the outage should not be sent afterwards.
- **API pods** (loads-app api, thrs-control api, domestic-control backend): MQTT is optional for readiness, as for mqtt-graphql.
- **data-gen** produces test data. Is it worth converting at all?

## F5: vector

The `mqtt` source does not re-subscribe when the broker has lost the session (upstream: vectordotdev/vector#26730). The fix is our upstream PR [vectordotdev/vector#26731](https://github.com/vectordotdev/vector/pull/26731): it subscribes again when a reconnect's CONNACK has `session_present = 0`. It was merged on 2026-11-09 and is waiting for a release.

**Decided: the existing alert until #26731 is released, then upgrade Vector.** `VectorSourceNoEvents` in edge-flux (`infrastructure/shared/observability/rules/vector/vector.yml`) fires after about 6 min without MQTT intake and pages through Alertmanager to PagerDuty. Until then, a human restarts Vector. No liveness probe or sidecar: an intake check can't tell a stuck source from a quiet one or a broker outage, so it would restart healthy pods. Known gap: a source that has never received anything never fires.

**This is a temporary exception to the ADR's 15 minute deadline:** a stale source keeps Vector `Running` until a human restarts it. Owner: Floris Smit. It ends when #26731 is released and Vector is upgraded; until then the alert bounds how long it goes unnoticed, not how long it lasts.

## Not in this plan

These are outside the ADR's scope, but the work above touches them:

- **Replay policy:** which buffered data is sent after an outage. Telemetry should be; commands should not.
- **QoS 1 in-flight messages:** these can be lost or duplicated on reconnect. For telemetry stamped with `TimeStamp` that is probably acceptable.
- **Alerting:** pods not ready for more than about 5 min, restarts caused by the 15 min deadline, and readings dropped because the #716 buffer filled.
- **zero-ui offline detection** on the client side: suggested for a separate ticket.

## Order

Python, in [ZERO-2605](https://foundationzero-team.atlassian.net/browse/ZERO-2605), one PR each on top of the previous:

1. **This ADR amendment and plan.**
2. **`zero-health`** in `packages/py`.
3. **`zero-mqtt`** in `packages/py`: the broker defaults, the refusal wrapper (moved from the bridge) and the ping check.
4. **F1:** move `zero-modbus-bridge` into `packages/py`, wire `zero-health` into power-tags, termodinamica and hull-temperature, and switch their charts to HTTP probes.
5. **F2:** atpx-nmea, with both brokers required.

Then:

1. **Rust, in [ZERO-2612](https://foundationzero-team.atlassian.net/browse/ZERO-2612):** move the identical `readiness.rs` of battery-cells and fiber-optics into one crate in `packages/rust`, keeping the status file and exec probe.
2. **Upstream:** drop the `zero-mqtt` wrapper once zMQTT#129 is released (ZERO-2532); follow rumqtt#1078; upgrade Vector once vector#26731 is released.
3. **F4:** in ZERO-2531.

**Verification for each step:** the test from ZERO-2406. On singel, delete all RabbitMQ pods and check that every converted app:
- shows `0/1 Running` with the reason in `kubectl describe`,
- reconnects within about 1 min of the broker being Ready, without restarting.

Then keep the broker down for more than 15 min and check that the pods restart once and do not enter `CrashLoopBackOff`.
