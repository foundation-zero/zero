# Plan: apply ADR 0001 to the zero apps

Temporary: delete this file when the work is done. The rules are in [ADR 0001](../adr/0001-dependency-outages.md); the trigger and outage notes are in [ZERO-2406](https://foundationzero-team.atlassian.net/browse/ZERO-2406).

**Keep it 80/20.** Prefer the simplest change that fixes the actual outage behaviour over full conformance to every rule. Where meeting a rule would mean a large change for little benefit, stop and flag it with the simpler alternative instead of building it.

## Where we are

Two ways the apps break the ADR today:

- **Stuck:** the app stays `Running` without a broker connection until someone restarts it. It loses data silently. This happened in the 2026-10-13 RabbitMQ cutover.
- **Crash:** the app exits when the broker goes away and comes back through `CrashLoopBackOff`. That is safe, but it is red in k9s and adds minutes of restart backoff.

No app reports MQTT connectivity through readiness, and none has the 15 min deadline.

## Flavours

| Flavour | Apps | Today | Main work |
| --- | --- | --- | --- |
| **F1** FastStream/zmqtt through `zero-modbus-bridge` | power-tags, termodinamica, hull-temperature | Stuck (hull-temperature: expected since #716, not observed) | Fix zmqtt give-up handling once, in the bridge |
| **F2** FastStream/zmqtt, standalone | atpx-nmea | Stuck | Same as F1, plus a second broker and a zmqtt/FastStream upgrade |
| **F3** rumqttc (Rust) | fiber-optics, battery-cells, mqtt-graphql | fiber-optics stuck; the other two reconnect | Readiness and deadline; diagnose fiber-optics |
| **F4** aiomqtt, exits on error | loads-app (api, control), thrs-control (control, simulation, api), domestic-control, data-gen | Crash | Replace "exit on error" with a reconnect loop |
| **F5** third party | vector | Stuck (doesn't re-subscribe) | We can't change the client |

Out of scope: zero-ui (browser client), zero-generator (library, not deployed on its own), alert-forwarder (no MQTT), and sail-systems-mqtt-adapter (separate repo; needs its own ticket).

## Shared pieces

Every flavour needs the same three things:

- **Status file:** the app writes its readiness and the reason, e.g. `not ready: mqtt: CONNACK refused (server unavailable) since 13:02`.
- **Deadline:** after 15 min not ready, the app writes the reason to `/dev/termination-log` and exits.
- **Probe:** an exec readiness probe in each chart that prints the status file and fails when the app is not ready. All images are Debian slim, so `sh` is available.

Every flavour also has to meet these:

- **Backoff cap of 30 s.** All our clients cap at 60 s today: the three Rust apps, and zmqtt's default `max_delay`. With a 60 s cap a client can wait a full minute after the broker is back, which misses the "reconnect within about 1 min" target.
- **Keepalive of 15 s.** It detects a dead connection; RabbitMQ's keepalive window races the 60 s default (see power-tags).
- **Permanent errors such as bad credentials:** retry a few times, then exit (ADR). The Rust clients retry these forever today, so only the 15 min deadline would stop them.
- **Required or optional:** each app decides this for each of its dependencies, not only MQTT. Examples: Postgres for loads-app and thrs-control, Home Assistant and Modbus for domestic-control.

Things to know before rolling this out:

- **k9s colours `0/1 Running` the same red as `CrashLoopBackOff`.** Only the STATUS text differs, so a broker outage will still look red. It just won't restart pods.
- **A rollout stalls while a required dependency is down,** because new pods never become ready. It resumes once the dependency is back.

**Choice: where the shared code lives.**
- **Python:** F1 already shares `zero-modbus-bridge`; F2 and F4 don't depend on it. The options are a small new shared package, or putting it in `zero-modbus-bridge` and adding it as a dependency of the others, or a copy per app (about 50 lines).
- **Rust:** a shared crate, or a copy in each of the three apps.
- **Charts:** there is no shared chart library, so the probe snippet is copied into each chart either way.

## F1: power-tags, termodinamica, hull-temperature

Requirements:
- **Confirm the root cause first.** The zmqtt explanation below comes from reading the library code. Check it against the logs from the 2026-10-13 outage before building on it. hull-temperature's stuck state is predicted from #716, not observed.
- **CONNACK refusals:** zmqtt does not retry them, even with `max_attempts=None`, and that ends its reconnect task. The ADR asks for "retry a few times, then exit", because RabbitMQ refuses connections while it boots.
- **Give-up:** exit from `on_connection_recovery_failed` (zmqtt ≥0.2 and FastStream 0.7.5 have it).
- **Defaults** in `MqttSettings.make_broker`: `ReconnectConfig(max_attempts=None)` and a 15 s keepalive. Today only power-tags sets them.

Choices:
- **How to fix CONNACK refusals:** fix zmqtt upstream and wait for a release, or wrap the client in the bridge so it retries refusals a few times before exiting. Exiting on the first refusal is not an option: the ADR requires retrying first, because a booting broker refuses connections.
- **Modbus gateways, required or optional?** power-tags reads many gateways. If one gateway is down, the pod is still doing most of its job, so that gateway is probably optional and only logged. termodinamica and hull-temperature each read a single gateway, so it is probably required.
- **Replay buffer (#716):** the ADR leaves replay out of scope. hull-temperature also publishes a relay command, which should not be replayed after an outage. Does that need its own ticket?

## F2: atpx-nmea

Requirements:
- **zmqtt and FastStream upgrade:** zmqtt from 0.1.1 to ≥0.2.2 and FastStream from 0.7.4 to ≥0.7.5 (raise the minimum in `pyproject.toml` and update `uv.lock`), to get `on_connection_recovery_failed`.
- **Both brokers:** the same handling as F1 for the A+T input broker and the RabbitMQ output broker.

Choice:
- **Is the A+T input broker required?** Without it the pod has nothing to do, so yes, it would show `0/1` whenever A+T's broker is down. That is outside our control, but it is the honest signal.

## F3: fiber-optics, battery-cells, mqtt-graphql

Requirements:
- **fiber-optics:** reproduce the outage on singel with rumqttc 0.25 before changing anything. Whatever the cause, "connected" must mean PUBACKs are coming back, not that the TCP connection is open. Rule out a RabbitMQ memory or disk alarm, which blocks publishers while TCP stays up.
- **battery-cells and mqtt-graphql:** these already reconnect, and mqtt-graphql re-subscribes on every CONNACK. They only need the status file, the deadline and the probe.

Choices:
- **UDP input (fiber-optics, battery-cells):** these apps receive sensor data through a UDP `LoadBalancer` Service. A not-ready pod is removed from the Service, so incoming packets stop reaching it during an outage. Accept that (the packets can't be published anyway), or set `publishNotReadyAddresses: true` so the pod keeps receiving and can buffer.
- **HTTP API (mqtt-graphql):** a not-ready pod is removed from its Service, so the UI gets errors instead of values marked missing (#905). Is MQTT required for this pod's readiness, or optional, so it keeps serving and reports values as missing?

## F4: loads-app, thrs-control, domestic-control, data-gen

This is the largest behaviour change. aiomqtt has no automatic reconnect: the apps use `async with Client(...)`, and an `MqttError` ends the process. loads-app and thrs-control exit on purpose with `sys.exit(1)` (`loads/api/dependencies.py`, `thrs/graphql/strawberry.py`).

Requirements:
- **A reconnect loop** around the client, with the 30 s backoff cap and 15 s keepalive. Subscriptions are set up again after each reconnect.
- **Keep thrs-control's heartbeat liveness probe.** It checks the control loop, not MQTT, so it already fits the ADR.

Choices:
- **Priority:** these apps recover today, just slowly and noisily. Do them in this ticket, or in a follow-up?
- **Controllers** (thrs-control, domestic-control, loads control): waiting inside the process keeps control state across an outage, and a restart starts from a clean state. Which do we want? Commands queued during the outage should not be sent afterwards.
- **API pods** (loads-app api, thrs-control api, domestic-control backend): same question as mqtt-graphql. If MQTT is required for readiness, the API drops out of its Service during a broker outage. loads-app api already checks Postgres for readiness; is MQTT required there too?
- **data-gen** produces test data. Is it worth converting at all?

## F5: vector

The `mqtt` source does not re-subscribe when the broker has lost the session (upstream: vectordotdev/vector#26730). We can't fix this in the app.

Choices:
- **Detection:** a readiness probe that checks MQTT intake through Vector's API or internal metrics, an alert on intake at 0, or both.
- **Recovery:** with the 15 min rule the pod must also restart, so readiness alone isn't enough. Vector can't exit on its own, so this means either a liveness probe that fails after 15 min without MQTT intake (the ADR allows liveness for a deadline the app can't enforce), or a small sidecar that restarts it. Or we accept a manual restart until upstream fixes it.
- **Upstream:** wait, or contribute the fix ourselves?

## Not in this plan

These are outside the ADR's scope, but the work above touches them:

- **Replay policy:** which buffered data is sent after an outage. Telemetry should be; commands should not.
- **QoS 1 in-flight messages:** these can be lost or duplicated on reconnect. For telemetry stamped with `TimeStamp` that is probably acceptable.
- **Alerting:** pods not ready for more than about 5 min, restarts caused by the 15 min deadline, and readings dropped because the #716 buffer filled.

## Suggested order

0. **Optional stopgap:** add only the status file, the 15 min deadline and the probe to the stuck apps. That caps the damage at 15 min per outage while the client fixes are being built.
1. **F1 and F2:** they are stuck today and share the zmqtt fix. This also builds the Python helper.
2. **fiber-optics diagnosis and vector detection:** both are stuck today. The diagnosis can run in parallel with step 1.
3. **F3:** the Rust helper, battery-cells and mqtt-graphql.
4. **F4:** only if we agree to do it in this ticket.

**Verification for each step:** the test from ZERO-2406. On singel, delete all RabbitMQ pods and check that every converted app:
- shows `0/1 Running` with the reason in `kubectl describe`,
- reconnects within about 1 min of the broker being Ready, without restarting.

Then keep the broker down for more than 15 min and check that the pods restart once and do not enter `CrashLoopBackOff`.
