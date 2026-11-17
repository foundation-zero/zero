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

Every flavour needs readiness, the 15 min deadline and a probe. How depends on the app:

- **FastStream apps (F1, F2):** serve `/health` from FastStream itself: `AsgiFastStream` with `make_ping_asgi(broker)`, which returns 204, or 500 when `broker.ping()` fails. An app with more than one required dependency (a second broker, a Modbus gateway) writes a small handler that checks each one. The chart points both probes at `/health`: readiness with the usual short period, liveness with `periodSeconds: 60` and `failureThreshold: 15`, which is the deadline (ADR). The app logs every readiness change with the reason.

  Things to know, from a local test against a stopped broker:
  - The HTTP server is up before the broker connects, so `/health` answers 500 while the client retries; it turns 204 on the first successful reconnect.
  - `broker.ping()` sends a real PINGREQ; on a silent broker it takes its full timeout (4 s), so keep the probe's `timeoutSeconds` above that.
  - Pass `host="0.0.0.0"` and a port through `run_extra_options`; uvicorn defaults to 127.0.0.1, which the kubelet can't reach. Set `access_log=False`, or every probe is logged.
- **Rust apps (F3):** a status file the app writes, e.g. `not ready: mqtt: CONNACK refused (not authorized) since 13:02`, on an `emptyDir` mount because the charts set `readOnlyRootFilesystem`; an exec readiness probe that prints it; and an in-process deadline that writes the reason to `/dev/termination-log` and exits. Done in phase 1; the shared code is the `zero-readiness` crate in `packages/rust` (ZERO-2612).

Every flavour also has to meet these:

- **Backoff cap of 30 s.** With zmqtt's and our Rust apps' old 60 s cap, a client could wait a full minute after the broker is back, which misses the "reconnect within about 1 min" target. Done in phase 1.
- **Keepalive of 15 s.** It detects a dead connection; RabbitMQ's keepalive window races the 60 s default. Done in phase 1.
- **Refusals, permanent errors such as bad credentials:** retry a few times, then exit (ADR). This includes 0x87, because RabbitMQ sends it while booting. Done in phase 1: the Python apps exit after about 90 s, the Rust apps after 10 refusals (about 3 min).
- **Required or optional:** each app decides this for each of its dependencies, not only MQTT. MQTT is required for worker pods and optional for pods that serve an HTTP API, so the API stays in its Service and reports values as missing (#905).

Things to know before rolling this out:

- **k9s colours `0/1 Running` the same red as `CrashLoopBackOff`.** Only the STATUS text differs, so a broker outage will still look red. It just won't restart pods.
- **A rollout stalls while a required dependency is down,** because new pods never become ready. It resumes once the dependency is back.

**Decided: no new packages for health.** The Python health code is a few lines per app on top of FastStream, so each app has its own; the F1 apps share theirs through `zero-modbus-bridge`, as they already share the broker setup. The zmqtt workaround (`RecoveringClient`) stays where phase 1 put it, in the bridge and a copy in atpx-nmea, until the upstream fixes are released. There is no shared chart library, so the probe block is copied into each chart.

## F1: power-tags, termodinamica, hull-temperature

Done in #974: `make_broker` sets `max_attempts=None`, the 30 s cap and the 15 s keepalive, exits from `on_connection_recovery_failed`, and wraps the client in `RecoveringClient`. The wrapper retries CONNACK refusals and catches two ways zmqtt's run loop dies silently. All three apps use it.

Left:
- **Health:** `AsgiFastStream` with `/health` and both probes, as above.
- **Modbus gateways:** optional (logged only) for power-tags, which reads many; required for termodinamica and hull-temperature, which each read one, so their `/health` also checks the gateway.

Upstream:
- **Refusals:** fixed in zMQTT#129, released in zmqtt 0.2.6. ZERO-2532 bumps zmqtt and drops that part of the wrapper.
- **Silent run-loop exits:** a broker that closes the connection before CONNACK, and a protocol error, end zmqtt's run loop without calling `on_connection_recovery_failed` (zMQTT#135, #136; fix in zMQTT#137). Once released, `RecoveringClient` goes away.

Open:
- **Replay buffer (#716):** the ADR leaves replay out of scope. hull-temperature also publishes a relay command, which should not be replayed after an outage. Does that need its own ticket?

## F2: atpx-nmea

Done in #977: the zmqtt and FastStream upgrade, and the F1 handling for both brokers, through a copy of the bridge's `mqtt.py`.

Left:
- **Health:** `AsgiFastStream` with a `/health` handler that checks both brokers, and both probes.
- **Verification** also covers an outage of the A+T input broker. That broker is outside our control, so simulate it rather than touch it.

Proposed: **the A+T input broker is required.** Without it the pod has nothing to do, so it shows `0/1` whenever A+T's broker is down. That is outside our control, but it is the honest signal.

## F3: fiber-optics, battery-cells, mqtt-graphql

**fiber-optics root cause:** it was our only app on rumqttc's MQTT 5 client, whose event loop writes and flushes the socket without a timeout (`rumqttc v5/eventloop.rs`, 0.24 and 0.25; upstream issue [bytebeamio/rumqtt#1078](https://github.com/bytebeamio/rumqtt/issues/1078)). The MQTT 3.1.1 client wraps the flush in a timeout. In the cutover RabbitMQ's pod IP disappeared without a TCP reset, fiber-optics' send buffer filled with ~16 KB publishes at 10 Hz, and the flush never returned. No error was logged, and the keepalive check never ran. There was no RabbitMQ memory or disk alarm.

Done: battery-cells (#971) and fiber-optics (#976, now on the MQTT 3.1.1 client) report readiness through a status file and exit on the deadline; their shared code is the `zero-readiness` crate (#1020). mqtt-graphql (#975) caps its backoff and exits on refusals; its MQTT is optional, so it has no readiness.

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

The `mqtt` source does not re-subscribe when the broker has lost the session (upstream: vectordotdev/vector#26730). The fix is our upstream PR [vectordotdev/vector#26731](https://github.com/vectordotdev/vector/pull/26731): it subscribes again when a reconnect's CONNACK has `session_present = 0`. It was released in Vector 0.62.0.

**Decided: the existing alert until Vector is upgraded to 0.62 (ZERO-2533).** `VectorSourceNoEvents` in edge-flux (`infrastructure/shared/observability/rules/vector/vector.yml`) fires after about 6 min without MQTT intake and pages through Alertmanager to PagerDuty. Until then, a human restarts Vector. No liveness probe or sidecar: an intake check can't tell a stuck source from a quiet one or a broker outage, so it would restart healthy pods. Known gap: a source that has never received anything never fires.

**This is a temporary exception to the ADR's 15 minute deadline:** a stale source keeps Vector `Running` until a human restarts it. Owner: Floris Smit. It ends when Vector is upgraded; until then the alert bounds how long it goes unnoticed, not how long it lasts.

## Not in this plan

These are outside the ADR's scope, but the work above touches them:

- **Replay policy:** which buffered data is sent after an outage. Telemetry should be; commands should not.
- **QoS 1 in-flight messages:** these can be lost or duplicated on reconnect. For telemetry stamped with `TimeStamp` that is probably acceptable.
- **Alerting:** pods not ready for more than about 5 min, restarts caused by the 15 min deadline, and readings dropped because the #716 buffer filled.
- **zero-ui offline detection** on the client side: suggested for a separate ticket.

## Order

Phase 1 (reconnects for all flavours, Rust readiness) is done. Python health, in [ZERO-2605](https://foundationzero-team.atlassian.net/browse/ZERO-2605):

1. **This ADR amendment and plan.**
2. **zmqtt 0.2.6** (ZERO-2532): bump it and drop the refusal retry from `RecoveringClient`.
3. **F1:** `/health` and both probes for power-tags, termodinamica and hull-temperature.
4. **F2:** the same for atpx-nmea, both brokers required.

Then:

1. **Upstream:** delete `RecoveringClient` once zMQTT#137 is released; follow rumqtt#1078; upgrade Vector to 0.62 (ZERO-2533).
2. **F4:** in ZERO-2531.

**Verification for each step:** the test from ZERO-2406. On singel, delete all RabbitMQ pods and check that every converted app:
- shows `0/1 Running`, with the reason in `kubectl describe` (exec probes) or the app logs (HTTP probes),
- reconnects within about 1 min of the broker being Ready, without restarting.

Then keep the broker down for more than 15 min and check that the pods restart once and do not enter `CrashLoopBackOff`.
