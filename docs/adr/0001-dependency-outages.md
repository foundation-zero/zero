# Pods wait out dependency outages instead of crashing

A pod either does its job or reports itself not ready. It never shows `Running` while it is silently cut off from something it needs.

## Rules

Each service decides which of its dependencies (MQTT broker, database, Modbus gateway, …) are **required** and which are **optional**. A required dependency is one without which the pod cannot do its job. Only required dependencies affect readiness. When an optional dependency is unavailable, the pod logs it and retries, and stays ready.

- **Required dependency unavailable** (down, refusing connections, connection dropped), at startup or later: stay up, retry with capped backoff, and fail the readiness probe. The pod shows as `0/1 Running`.
- **Client gives up** (the library stops retrying, or its reconnect task dies): exit immediately. If the app cannot notice this itself (the client stalls without raising an error, or the client is third-party code), use a liveness probe instead (see below).
- **Permanent error** (bad credentials, unknown host, malformed configuration): retry a few times, then exit. Some of these errors are temporary (a broker can refuse logins while it boots), so do not exit on the first one. They must still end the container well within 15 minutes (see below).
- **Not ready for 15 minutes:** restart. Either the app exits by itself, or a liveness probe on the same check as readiness fails 15 times in a row (`periodSeconds: 60`, `failureThreshold: 15`) and Kubernetes restarts the container. This is a safety net for failures the pod cannot detect itself. It is 15 minutes, not 10, because the kubelet only resets its restart backoff once a container has run for more than 10 minutes, so these restarts never add up to `CrashLoopBackOff`.
- **Liveness checks the process and its own clients**, not whether a dependency is reachable. The one exception is the 15 minute restart above. Most pods need no liveness probe, because they can exit on their own. Add one where the process can hang without exiting, such as a blocked event loop or a client that has silently stopped reconnecting. A blocked event loop also fails the 15 minute probe above, so a pod with that probe needs no second one.
- **Report the reason.** The app logs each change in readiness, with the dependency and why it is unavailable. An exec probe also prints it, and `kubectl describe` shows that output in the pod events. Kubernetes discards the body of an HTTP probe response, so with an HTTP probe the reason is only in the logs. An app that exits by itself writes the reason to its termination message.

## Defining "ready"

What counts as ready depends on the dependency. Suggestions, not requirements:

- **Long-lived connections** (MQTT): ready while the client is connected. Read the client's own connection state, or send an MQTT ping (PINGREQ), which is what FastStream's `broker.ping()` does. Nothing heavier on every probe.
- **Pooled or per-request connections** (databases): ready while the most recent query or connection attempt succeeded. Optionally add a cheap periodic check (`SELECT 1`) when there is little traffic.
- **Probe type:** use the framework's own health endpoint where there is one, such as FastStream's `make_ping_asgi`. Pods without an HTTP server can use an exec probe that reads a status file the app writes.

## Considered options

**Crash when a dependency is unavailable, and let Kubernetes restart the pod.** This is simpler, and restarting does clear a client stuck in a bad state. We rejected it for two reasons. First, restart backoff grows to 5 minutes, which delays recovery once the dependency is back. Second, an outage of one shared dependency puts every pod that uses it into `CrashLoopBackOff`, which hides the pod that is actually broken.

**Check dependencies in the liveness probe.** We rejected this for the same reasons. A liveness probe that checks a shared dependency and fails within seconds restarts every pod that uses it at the same moment. Two kinds of liveness probe avoid that. One checks the pod's own client, so it fails only in the pod whose client is stuck. The other fails only after 15 minutes, so it restarts the pod at the same time as an app that exits by itself would.

## Out of scope

Buffering or replaying data during an outage, and alerting on not-ready pods, are separate decisions.
