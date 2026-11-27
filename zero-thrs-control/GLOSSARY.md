# Heat system control

Controls the Heat system through the AMCS: reads Sensor values from it, sends it Commands and reads back the Actuated values.

## Language

**Heat system**:
The ship's thermal installation, HS for short, that Heat system control controls through the AMCS.
_Avoid_: THRS (Thermal Harvesting & Recovery System, its old name), thermal system

**Heat system control**:
The software in this service. The code, the repository and the deployment still say THRS control, and will follow.
_Avoid_: THRS control (in new names and text)

**AMCS**:
The Alarming, Monitoring and Control System: the ship's automation system (Marpower). It owns the components. Heat system control sends it Commands, which it follows only in Advisory mode.
_Avoid_: PLC, plant (the plant is what the AMCS runs)

**Module**:
One part of the Heat system, such as pcm, dhw or cooling. Heat system control is made up of independent modules. Most have Sensor values, MQTT topics and an AMCS mode; high_temperature exists only in simulation.
_Avoid_: Subsystem

**Control module**:
A module Heat system control also controls: it has Control values, Parameters, an Automatic control and a Controller state, and with them an Automation mode and Manual values. Not every module is one; cooling has no control yet.
In code, `Module` and `ModuleDescription` in `orchestration/module.py`; `Module` always means a Control module.

**AMCS mode**:
Per module, which of its modes the AMCS is in, deciding where it takes its values from: `LOCAL`, `MANUAL`, `AUTO` or `EXTERNAL`. Heat system control only checks whether it is `EXTERNAL`, Advisory mode. The AMCS's `MANUAL` and `AUTO` are its own and unrelated to the Automation mode.
In code, `AmcsMode`, held by the component `AmcsModeStatus`, in `input_output/definitions/system.py`.
_Avoid_: Control mode (that is the Automatic control's state)

**Advisory mode**:
The one AMCS mode in which the AMCS follows a module's Commands. The AMCS documentation calls it advisory, its code `EXTERNAL`; Heat system control says advisory throughout and maps `EXTERNAL` to it only where it models the AMCS. Outside Advisory mode, a Control module's Automation mode is manual and its Manual values follow the Actuated values every tick.
In code, `AmcsModeStatus.is_advisory`.
_Avoid_: External mode

**Automation mode**:
Per Control module, whether Heat system control sends what its Automatic control computes or the Manual values: `automatic` or `manual`. Leaving Advisory mode switches it to manual, and it stays manual when the AMCS returns to advisory, until a user switches it back.
In code, `AutomationMode` in `control/state.py`, its values typed `ControlModes`.
_Avoid_: AMCS mode, control mode

**Automatic control**:
The part of a Control module that computes Control values from Sensor values and Parameters, run while its Automation mode is automatic. It is built afresh each time automatic starts.
In code, `Control` in `classes/control.py`, built by `Switching` in `control/switching.py`.

**Control mode**:
The state a Control module's Automatic control is in, such as the PCM charging; `None` while manual.
In code, `ControlMode` in `control/state.py`, subclassed per module (`PcmControlMode`), and `ControlState.control_mode`.
_Avoid_: AMCS mode; `CC_ControlMode` (a Setpoint of a pump)

**Component**:
A part of a module's values with its own MQTT topic: a valve, pump or sensor, but also the AMCS mode or the Heartbeat. Most stand for one device on board.
_Avoid_: Device (the physical thing; in code only the topic root, `mqtt_devices_topic_prefix`)

**Control values**:
A Control module's values for its components, as sent to the AMCS in Commands. They come in three kinds of one shape: what its Automatic control computes, sent while automatic; the Manual values, sent while manual; and the Actuated values, which the AMCS reports back.
In code, `*ControlValues`, for example `PcmControlValues`; Manual and Actuated values have the same type.
_Avoid_: Computed values (`send_computed_values` publishes values computed from Sensor values)

**Command**:
The values Heat system control sends the AMCS for one component, on that component's topic with the `Command` suffix: its Setpoints, or the Heartbeat. A module's Commands go out per component, not as one message.
_Avoid_: Control message

**Setpoint**:
One field a component is set to, such as a valve's position or a pump's dutypoint or on/off. The component may take a while to get there: a valve set to open can take more than a minute to finish actuating.
In code, for example `Valve.setpoint`, `Pump.dutypoint` and `Pump.on`.
_Avoid_: Target

**Target**:
What a PID controller works towards, such as a supply temperature. A PID controller turns it into a Setpoint for its actuator (the component it acts on).
In code, `PidControllerValues.target`.
_Avoid_: Setpoint

**Parameters**:
The settings of a Control module's Automatic control that a user can change while it runs, such as Targets and PID tunings. They start from their class's defaults.
In code, `*Parameters`, for example `PcmParameters`.

**Controller state**:
What a Control module publishes about its control: its Automation mode, Manual values, Control mode and Parameters, plus its controllers, such as PID controllers, as components.
In code, `ControlState` in `control/state.py`, subclassed per module (`PcmControllerState`).

**Heartbeat**:
The `external_available` component of every Control module's Control values, sent on its own Command topic with every other Command. A module sends no Commands until its first complete Actuated values are in, so neither does it send the Heartbeat: the AMCS never sees one without control behind it. The AMCS's Watchdog monitors it.
In code, `AmcsExternalAvailable` on `AmcsHeartbeatControlValues`.
_Avoid_: Watchdog (that is the monitor, not the signal), keep-alive

**Watchdog**:
The AMCS's monitor of the Heartbeat. For now it waits forever; soon it will work as a real watchdog and take a module out of Advisory mode when the Heartbeat stops. Its timeout then has to cover a restart plus the wait for the first Actuated values, which the AMCS may publish only about once a minute when nothing changes.

**Actuated values**:
The Control values the AMCS reports it applied: per component its Setpoints, on the component's own topic without a suffix. For valves and pumps they are in the payload fields named `CC_…` (`CC_Setpoint`, `CC_DutyPoint`, …), for other components in the plain fields. They say what a component was set to, not that it got there. They arrive on the same topics as the Sensor values, so a complete set of Sensor values implies complete Actuated values.
In code, `ControlChannels.get_actuated_control_values`.
_Avoid_: Echo, feedback, readback

**Sensor values**:
A module's measurements from the AMCS, its AMCS mode among them. Like every partial MQTT mapping, they are `None` until the first complete set arrives and never `None` again: code that handles missing Sensor values only runs at startup, never after a dropout.
_Avoid_: Measurements, inputs (inputs are the simulation's)

**Manual values**:
The Control values a Control module sends while its Automation mode is manual. They follow the Actuated values, whatever the AMCS or the Automatic control last applied: every tick outside Advisory mode, on the tick automatic hands over to manual, and from the first complete Actuated values after a restart. Otherwise they change only when a user sets them.
_Avoid_: Defaults

**Initial values**:
Control values or Controller state at their starting point: each unit's zero, except where a field's `initial_value` or a class's `initial()` override sets otherwise. They are what control starts from, not what it sends after a restart.
In code, `ThrsValues.initial()`.
_Avoid_: Zero values, defaults

**Lockstep**:
Simulation and control ticking in one process, the simulation fed the Control values directly. Because they tick together, nothing waits for startup values, and as a simulation nothing real can break, so its startup values hardly matter.
In code, `LockstepRunner` in `runtime/runners/lockstep.py`.
_Avoid_: Co-simulation

**Co-simulation**:
Several FMUs coupled into one simulation that behaves like a single FMU, fields of one feeding fields of another.
In code, `CoSimulationMaster` and `Coupling` in `simulation/cosimulation.py`.
_Avoid_: Lockstep
