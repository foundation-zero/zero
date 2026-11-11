# Pods wait out dependency outages instead of crashing

A pod either does its job or reports itself not ready. It never shows `Running` while it is silently cut off from something it needs.

## Rules

Each service decides which of its dependencies (MQTT broker, database, Modbus gateway, …) are **required** and which are **optional**. A required dependency is one without which the pod cannot do its job. Only required dependencies affect readiness. When an optional dependency is unavailable, the pod logs it and retries, and stays ready.

- **Required dependency unavailable** (down, refusing connections, connection dropped), at startup or later: stay up, retry with capped backoff, and fail the readiness probe. The pod shows as `0/1 Running`.
- **Client gives up** (the library stops retrying, or its reconnect task dies): exit immediately. If the app cannot notice this itself (the client stalls without raising an error, or the client is third-party code), use a liveness probe instead (see below).
- **Permanent error** (bad credentials, unknown host, malformed configuration): retry a few times, then exit. Some of these errors are temporary (a broker can refuse logins while it boots), so do not exit on the first one. They must still end the container well before the 15 minute deadline.
- **Not ready for 15 minutes** (configurable, but always above 10 minutes): exit. This is a safety net for failures the pod cannot detect itself. The deadline is 15 minutes, not 10, because the kubelet only resets its restart backoff once a container has run for more than 10 minutes. Exits on this deadline therefore never add up to `CrashLoopBackOff`.
- **Liveness checks the process and its own clients**, never whether a dependency is reachable. Most pods need no liveness probe, because they can exit on their own. Add one where the process can hang without exiting, such as a blocked event loop or a client that has silently stopped reconnecting, or where the app cannot enforce the 15 minute deadline itself. Such a probe fails only when the client is stuck or that deadline has passed; while the client is still retrying, the pod is alive.
- **Report the reason.** The app logs every change in readiness with the dependency and the reason, and the readiness probe returns them in its output. The termination message names them when the app exits, so `kubectl describe` shows why the last container ended. The kubelet copies exec probe output into the pod events but drops HTTP response bodies, so for an HTTP probe the events show only the status.

## Defining "ready"

What counts as ready depends on the dependency. Suggestions, not requirements:

- **Long-lived connections** (MQTT): ready while the client is connected. A check may ping the broker where the client offers it (FastStream's `broker.ping()`), which also catches a connection that is open but no longer answers. Checks run on the app's own interval and the probe reads the last result, so a probe never waits on the network.
- **Pooled or per-request connections** (databases): ready while the most recent query or connection attempt succeeded. Optionally add a cheap periodic check (`SELECT 1`) when there is little traffic.
- **Probe type:** Python pods serve `/health/ready` and `/health/alive` over HTTP from the shared `zero-health` package (`packages/py`): HTTP health endpoints like FastStream's, but the probe reads a cached result. `/health/alive` is a plain 204 served on the app's event loop, so a blocked loop times it out; the in-process deadline cannot fire in a blocked loop. Pods without an HTTP server, such as battery-cells and fiber-optics, may keep an exec probe that reads a status file the app writes.

## Considered options

**Crash when a dependency is unavailable, and let Kubernetes restart the pod.** This is simpler, and restarting does clear a client stuck in a bad state. We rejected it for two reasons. First, restart backoff grows to 5 minutes, which delays recovery once the dependency is back. Second, an outage of one shared dependency puts every pod that uses it into `CrashLoopBackOff`, which hides the pod that is actually broken.

**Check dependencies in the liveness probe.** We rejected this for the same reasons. A liveness probe that checks a shared dependency restarts every pod that uses it at the same moment. A liveness probe on the pod's own client is different: it fails only in the pod whose client is stuck, or after the same 15 minute deadline.

## Out of scope

Buffering or replaying data during an outage, and alerting on not-ready pods, are separate decisions.
