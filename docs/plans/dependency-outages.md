# Plan: apply ADR 0001 to the zero apps

Temporary: delete this file when the work is done. The rules are in [ADR 0001](../adr/0001-dependency-outages.md); the trigger and outage notes are in [ZERO-2406](https://foundationzero-team.atlassian.net/browse/ZERO-2406).

**Keep it 80/20.** Prefer the simplest change that fixes the actual outage behaviour over full conformance to every rule. Where meeting a rule would mean a large change for little benefit, stop and flag it with the simpler alternative instead of building it.

## Where we are

Three ways the apps break the ADR today:

- **Stuck:** the app stays `Running` without a broker connection until someone restarts it. It loses data silently.
- **Crash:** the app exits when the broker goes away and comes back through `CrashLoopBackOff`. That is safe, but it is red in k9s and adds minutes of restart backoff.
- **Slow:** the app reconnects by itself, but its 60 s backoff cap delays it by up to a minute after the broker is back.

No app reports MQTT connectivity through readiness, and none has the 15 min deadline.

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

Every flavour needs the same three things:

- **Status file:** the app writes its readiness and the reason, e.g. `not ready: mqtt: CONNACK refused (not authorized) since 13:02`. All charts set `readOnlyRootFilesystem`, so the file lives on an `emptyDir` mount (for example `/run/health`), with its path passed in through config.
- **Deadline:** after 15 min of continuous not-ready time, the app writes the reason to `/dev/termination-log` and exits. The timer resets whenever the app becomes ready. `/dev/termination-log` is writable without extra configuration.
- **Probe:** an exec readiness probe in each chart that prints the status file and fails when the app is not ready. All images are Debian slim, so `sh` is available.

Every flavour also has to meet these:

- **Backoff cap of 30 s.** All our clients cap at 60 s today: the three Rust apps, and zmqtt's default `max_delay`. With a 60 s cap a client can wait a full minute after the broker is back, which misses the "reconnect within about 1 min" target.
- **Keepalive of 15 s.** It detects a dead connection; RabbitMQ's keepalive window races the 60 s default (see power-tags).
- **Refusals, permanent errors such as bad credentials:** retry a few times over about 60–90 s, then exit (ADR). This includes 0x87, because RabbitMQ sends it while booting. The Rust clients retry these forever today, so only the 15 min deadline would stop them.
- **Required or optional:** each app decides this for each of its dependencies, not only MQTT. MQTT is required for worker pods and optional for pods that serve an HTTP API, so the API stays in its Service and reports values as missing (#905).

Things to know before rolling this out:

- **k9s colours `0/1 Running` the same red as `CrashLoopBackOff`.** Only the STATUS text differs, so a broker outage will still look red. It just won't restart pods.
- **A rollout stalls while a required dependency is down,** because new pods never become ready. It resumes once the dependency is back.

**Decided: the shared code is copied per app** (about 50 lines). The F1 apps get it once, in `zero-modbus-bridge`; every other app has its own copy, Python and Rust alike. There is no shared chart library, so the probe snippet is copied into each chart.

## F1: power-tags, termodinamica, hull-temperature

Requirements:
- **CONNACK refusals:** zmqtt never retries them, even with `max_attempts=None`. On the first connect the app exits; during a reconnect the refusal ends zmqtt's reconnect task and leaves the pod `Running`. The bridge wraps the client so it retries every refusal a few times, on the first connect and on reconnect, then exits. The wrapper is temporary: drop it once zmqtt retries refusals itself (see below).
- **Give-up:** exit from `on_connection_recovery_failed` (zmqtt ≥0.2 and FastStream 0.7.5 have it).
- **Defaults** in `MqttSettings.make_broker`: `ReconnectConfig(max_attempts=None)`, the 30 s backoff cap and a 15 s keepalive. Today only power-tags sets the first two, and termodinamica gives up after the default 5 attempts.
- **Modbus gateways:** optional (logged only) for power-tags, which reads many; required for termodinamica and hull-temperature, which each read one.

Open:
- **zmqtt upstream fix:** neither MQTT spec says whether a client should retry a refusal. Clients differ: Paho, HiveMQ and aiomqtt retry every refusal; MQTT.js retries none unless you opt in; gmqtt retries only the "server unavailable"-type codes. RabbitMQ sends 0x87 while a vhost is still starting or a user's permissions aren't set up yet. Proposed: by default retry 3, 0x88, 0x89, 0x97 and 0x9F within `max_attempts`, plus an opt-in `ReconnectConfig` hook that decides per refusal, which we use to add 0x87.
- **Replay buffer (#716):** the ADR leaves replay out of scope. hull-temperature also publishes a relay command, which should not be replayed after an outage. Does that need its own ticket?

## F2: atpx-nmea

Requirements:
- **zmqtt and FastStream upgrade:** zmqtt from 0.1.1 to ≥0.2.2 and FastStream from 0.7.4 to ≥0.7.5 (raise the minimum in `pyproject.toml` and update `uv.lock`), to get `on_connection_recovery_failed`.
- **Both brokers:** the same handling as F1, copied from the bridge, for the A+T input broker and the RabbitMQ output broker.
- **Verification** also covers an outage of the A+T input broker. That broker is outside our control, so simulate it rather than touch it.

Proposed: **the A+T input broker is required.** Without it the pod has nothing to do, so it shows `0/1` whenever A+T's broker is down. That is outside our control, but it is the honest signal.

## F3: fiber-optics, battery-cells, mqtt-graphql

**fiber-optics root cause:** it is our only app on rumqttc's MQTT 5 client, whose event loop writes and flushes the socket without a timeout (`rumqttc v5/eventloop.rs`, 0.24 and 0.25; upstream issue [bytebeamio/rumqtt#1078](https://github.com/bytebeamio/rumqtt/issues/1078)). The MQTT 3.1.1 client wraps the flush in a timeout. In the cutover RabbitMQ's pod IP disappeared without a TCP reset, fiber-optics' send buffer filled with ~16 KB publishes at 10 Hz, and the flush never returned. No error was logged, and the keepalive check never ran. There was no RabbitMQ memory or disk alarm.

Requirements:
- **battery-cells** sets the Rust pattern: readiness from the client's own connection state, the status file, the deadline, the backoff cap, the keepalive and the probe. mqtt-graphql and fiber-optics copy it.
- **fiber-optics** moves to the MQTT 3.1.1 client, which has the flush timeout. It loses the MQTT 5 PUBACK reason codes, which only fed logs and metrics (#630), and uses `clean_session=true` instead of a session expiry of 0. "Connected" must not require a recent PUBACK while the app is idle.
- **mqtt-graphql:** MQTT is optional for readiness, so the API keeps serving and reports values as missing.
- **UDP input (fiber-optics, battery-cells):** a not-ready pod drops out of its UDP `LoadBalancer` Service, so packets stop reaching it during an outage. We accept that; the packets can't be published anyway.
- **Verification for fiber-optics:** fiber-optics isn't deployed on singel, and deleting RabbitMQ pods usually resets connections cleanly. Test locally against a TCP listener that answers CONNACK and then stops reading.

## F4: loads-app, thrs-control, domestic-control, data-gen

**Decided: a follow-up ticket.** These apps recover today, just slowly and noisily. aiomqtt has no automatic reconnect: the apps use `async with Client(...)`, and an `MqttError` ends the process. loads-app and thrs-control exit on purpose with `sys.exit(1)` (`loads/api/dependencies.py`, `thrs/graphql/strawberry.py`).

For that ticket:
- **A reconnect loop** around the client, with the 30 s backoff cap and 15 s keepalive. Subscriptions are set up again after each reconnect.
- **Keep thrs-control's heartbeat liveness probe.** It checks the control loop, not MQTT, so it already fits the ADR.
- **Controllers** (thrs-control, domestic-control, loads control): waiting inside the process keeps control state across an outage, and a restart starts from a clean state. Which do we want? Commands queued during the outage should not be sent afterwards.
- **API pods** (loads-app api, thrs-control api, domestic-control backend): MQTT is optional for readiness, as for mqtt-graphql.
- **data-gen** produces test data. Is it worth converting at all?

## F5: vector

The `mqtt` source does not re-subscribe when the broker has lost the session (upstream: vectordotdev/vector#26730). The fix is our upstream PR [vectordotdev/vector#26731](https://github.com/vectordotdev/vector/pull/26731): it subscribes again when a reconnect's CONNACK has `session_present = 0`. It is open and waiting for a maintainer's review.

**Decided: the existing alert until #26731 is released, then upgrade Vector.** `VectorSourceNoEvents` in edge-flux (`infrastructure/shared/observability/rules/vector/vector.yml`) fires after about 6 min without MQTT intake and pages through Alertmanager to PagerDuty. Until then, a human restarts Vector. No liveness probe or sidecar: an intake check can't tell a stuck source from a quiet one or a broker outage, so it would restart healthy pods. Known gap: a source that has never received anything never fires.

## Not in this plan

These are outside the ADR's scope, but the work above touches them:

- **Replay policy:** which buffered data is sent after an outage. Telemetry should be; commands should not.
- **QoS 1 in-flight messages:** these can be lost or duplicated on reconnect. For telemetry stamped with `TimeStamp` that is probably acceptable.
- **Alerting:** pods not ready for more than about 5 min, restarts caused by the 15 min deadline, and readings dropped because the #716 buffer filled.
- **zero-ui offline detection** on the client side: suggested for a separate ticket.

## Order

1. **F1 bridge and charts, and battery-cells:** they set the Python and Rust patterns.
2. **atpx-nmea, mqtt-graphql and fiber-optics:** they copy those patterns once reviewed.
3. **Upstream:** the zmqtt refusal fix, then drop the bridge wrapper once it is released; follow rumqtt#1078; get vector#26731 merged, then upgrade Vector.
4. **F4:** in its follow-up ticket.

**Verification for each step:** the test from ZERO-2406. On singel, delete all RabbitMQ pods and check that every converted app:
- shows `0/1 Running` with the reason in `kubectl describe`,
- reconnects within about 1 min of the broker being Ready, without restarting.

Then keep the broker down for more than 15 min and check that the pods restart once and do not enter `CrashLoopBackOff`.
