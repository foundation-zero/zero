# Zero

Onboard monitoring and control software for the yacht: telemetry ingest, domain apps, and the crew/engineering UI.

## Language

### Apps

**Loads**:
The app that compares measured loads against the targets of the current load case and raises alarms when they are exceeded. Audience: crew.

**Rig**:
The app that shows the structural state of the masts and standing rigging (bending, strain, deflection, rigging loads and temperatures) as raw measurements. Audience: engineers.
_Avoid_: Fiber Optics (as an app name), Mast Structure, Mast Deformation

### Measurement

**Fiber optics**:
The sensor system that measures strain, deflection, temperature and load along the masts and rigging. A measurement source, not a domain.
_Avoid_: using it as the name of an app or screen

**Rigging load**:
The tension in a standing-rigging element (e.g. V1, D1, forestay), per mast and side. A rigging load can be both a Loads concern (actual vs target) and a Rig concern (raw measurement).
_Avoid_: Fiber optic load

**Load case**:
A named sailing condition that defines target values for loads, per tack.
