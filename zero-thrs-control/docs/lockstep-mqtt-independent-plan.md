# Plan: lockstep independent of MQTT

Branch: `feature/lockstep-mqtt-independent`, based on `fix/lockstep-simulation`.

## Goal

Lockstep ticks simulation and control in memory at the requested playback rate (up to 100x).
MQTT publishing runs on its own wall-clock cadence and publishes the latest snapshot, so the
tick rate no longer depends on broker round trips and the MQTT load no longer depends on the
playback rate.

## Where we are

Measured on `fix/lockstep-simulation` against the local broker (`high_temperature` unless noted):

| | per tick | max playback rate |
|---|---|---|
| Publishing every tick (current branch) | ~43 ms | ~20x |
| Tick with publishing stubbed out, `high_temperature` | 14 ms (FMU step 6 ms) | ~70x |
| Tick with publishing stubbed out, `thrs` | 32 ms (FMU step 14 ms) | ~30x |

The stubbed numbers still include serialising every mapping, so a tick that skips
serialisation between snapshots is somewhat faster. 100x (10 ms per tick) is realistic for
`high_temperature`, not for the full `thrs` mode.

Sensor values (sim → control) and control values (control → sim) already pass in memory in
`LockstepRunner.tick` (`src/thrs/runtime/runners/lockstep.py`). What still ties the tick to MQTT:

1. **Actuated control values loop back through the broker.** `Module.execute_control`
   (`src/thrs/orchestration/module.py:107`) reads `self._channels.get_actuated_control_values()`.
   In lockstep these are the simulation's own publishes, received back from MQTT. Once
   publishing is decoupled, control would see stale actuated values. This is the only real data
   dependency on MQTT.
2. **Publishing happens inside the tick.** `Module.tick` calls `send_control_updates`, and
   `LockstepRunner.tick` calls `simulation_module.send_simulation_updates`. The status is
   republished after every played tick through the loop's `running` hook
   (`src/thrs/runtime/loop.py`, `_tick_running`).
3. **Inbound API commands are fine as they are.** Parameters, manual values, automation mode
   and simulation inputs are read from the connector's non-blocking cache in
   `sync_control_channels_state` / `sync_simulation_inputs`.

## Steps

### 1. Feed actuated control values in memory

- Give `Module.tick` / `Module.execute_control` an explicit `actuated_control_values`
  argument. `ControlRunner` keeps passing the MQTT value
  (`self._channels.get_actuated_control_values()`), so production is unchanged.
- `LockstepRunner` passes `sim_result.control_values.values.get(module.name)`. This is the
  same value that currently comes back over MQTT one tick later, only without the broker
  in between.

### 2. Split compute from publish in `Module`

- Split `Module.tick` into a compute step that returns the tick's sensor values, control
  values and controller state, and a publish step (today's `send_control_updates`).
- `Module.tick` remains compute followed by publish, so `ControlRunner` and production keep
  their behaviour.

### 3. Make `LockstepRunner.tick` MQTT-free

- `tick()`: sync inbound commands, step the simulation, compute each module, and persist
  (`persist_all` only writes on change or on a 60 s heartbeat). Keep the latest simulation
  result and per-module results as the snapshot.
- New `publish()`: sends the latest snapshot. That is `send_simulation_updates` plus each
  module's publish step plus the simulation status with the current simulation time. It is a
  no-op when no tick happened since the last publish.

### 4. Publisher task next to the loop

- For lockstep, `Runtime.start` starts a task that calls `runner.publish()` every publish
  interval while the loop is running.
- Publish once more when a step completes and when pausing, so the final state is visible
  and the step tests keep their outputs.
- Replace the per-tick `running` status republish from commit `0ceb3e63` with the
  publisher's status publish, which keeps `SimulationTime` current at the publish cadence.
- The tick itself is synchronous CPU work. The loop still awaits a `sleep` every iteration,
  so the publisher gets scheduled even when ticks run flat out. Verify this at 100x.

### 5. Publish interval setting

- Add a publish interval to `LockstepCmd`, as a pydantic-settings CLI flag with an env
  fallback. Default 1 s wall-clock. Lower it (e.g. 0.25 s) for a livelier stream at high
  playback rates.

### 6. Raise the playback rate limit

- `PlayMessage.playback_rate` validation: `le=10` → `le=100`
  (`src/thrs/runtime/messages.py:37`).
- zero-ui `SimulationActions.vue`: `:max="10"` → `100`.

## Consequences to accept or handle

- **MQTT consumers get snapshots.** One sample per publish interval. At 100x with a 1 s
  interval that is one sample per 100 sim-seconds, so history and plots get coarser and
  short events between snapshots are invisible. Timestamps stay simulation time.
- **Mutation confirmation latency.** `ControlMessaging` (`src/thrs/graphql/messaging.py`)
  waits until the published parameters, actuated values or control mode reflect the change.
  That now takes up to one publish interval plus one tick instead of about one tick. This
  stays within `WAIT_TIMEOUT = 5` as long as the interval stays well below 5 s.
- **Machine-state logging.** When enabled, it still writes to the database every tick. It is
  off in the local `.env`. Check it does not become the bottleneck when enabled.
- **Alarms** are still evaluated every tick in `execute_control`. That is fine; only their
  publication moves to the snapshot.

## Tests to update or add

- `tests/runtime/test_runners.py::test_lockstep_runner_ticks_and_publishes_channels`:
  publishing now happens in `publish()`, not in `tick()`.
- `tests/cli/test_cli.py::test_simulation_run_playback_rate` counts simulation-output
  messages in equal wall time. With a fixed publish cadence those counts are equal, so assert
  on how far the simulation time advanced instead.
- Step tests in `tests/cli/test_cli.py` rely on outputs after each step. They are covered by
  publishing on step completion.
- `tests/runtime/test_loop.py::test_loop_reports_running_after_each_played_tick` changes or
  moves with the status republish.
- New: `Module` compute without publish, lockstep using in-memory actuated values, publisher
  cadence (a fake clock or a short interval), and `publish()` being a no-op without a new
  tick.

## Verification

Use the same harness approach as on `fix/lockstep-simulation`: an isolated process with its
own topic prefixes (`MQTT_DEVICES_TOPIC_PREFIX=prof/sim MQTT_CONTROLLER_TOPIC_PREFIX=prof/ctl
MQTT_SIMULATOR_TOPIC_PREFIX=prof/simulator`), built with `setup_lockstep` from
`tests/cli/test_cli.py`.

- The achieved playback rate at 10x, 20x, 50x and 100x for `high_temperature` and `thrs`
  (simulation-time delta divided by wall-clock delta).
- The lockstep connector's incoming queue (`len(client.messages)`) stays flat.
- Mutation latency against a real API (`uvicorn thrs.graphql.asgi:app --port 8765`) with
  `pcmParameterSetPcmChargeFlow` stays below the publish interval plus a margin.

## Open decisions

1. **Wall-clock or simulation-time publish interval.** A wall-clock interval keeps the MQTT
   load constant; a simulation-time interval keeps the sample density constant but brings the
   load back at high rates. The recommendation is wall-clock.
2. **Where persistence runs.** Keep it in `tick()` (it is cheap unless something changed), or
   move it to `publish()` to keep the database entirely off the hot path.
