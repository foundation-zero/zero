# Pods wait out dependency outages instead of crashing

A pod either does its job or reports itself not ready. It never shows `Running` while it is silently cut off from something it needs.

## Rules

Each service decides which of its dependencies (MQTT broker, database, Modbus gateway, …) are **required** and which are **optional**. A required dependency is one without which the pod cannot do its job. Only required dependencies affect readiness. When an optional dependency is unavailable, the pod logs it and retries, and stays ready.

- **Required dependency unavailable** (down, refusing connections, connection dropped), at startup or later: stay up, retry with capped backoff, and fail the readiness probe. The pod shows as `0/1 Running`.
- **Client gives up** (the library stops retrying, or its reconnect task dies): exit immediately. If the app cannot notice this itself (the client stalls without raising an error, or the client is third-party code), use a liveness probe instead (see below).
- **Permanent error** (bad credentials, unknown host, malformed configuration): retry a few times, then exit. Some of these errors are temporary (a broker can refuse logins while it boots), so do not exit on the first one. Exit within a few minutes, not after an open-ended retry.
- **Liveness never checks a dependency.** It answers one question: would restarting this container fix it? A restart does not bring back a broker or a gateway, so a pod stays up for as long as the outage lasts. Most pods need no liveness probe, because they exit on their own. Add one only where the process can hang without exiting, such as a blocked event loop or a client that has silently stopped reconnecting, and make it check that process or client, not the dependency.
- **Report the reason.** The app logs when a required dependency becomes unavailable and when it is back, with the reason; the client library's own log lines count. An exec probe also prints the reason, and `kubectl describe` shows that output in the pod events. Kubernetes discards the body of an HTTP probe response, so with an HTTP probe the reason is only in the logs. An app that exits by itself writes the reason to its termination message.
- **A long outage is for alerting, not restarts.** A pod that stays not ready is a signal for a person to look at.

## Defining "ready"

What counts as ready depends on the dependency. Suggestions, not requirements:

- **Long-lived connections** (MQTT): ready while the client is connected. Read the client's own connection state, or send an MQTT ping (PINGREQ), which is what FastStream's `broker.ping()` does. Nothing heavier on every probe.
- **Pooled or per-request connections** (databases): ready while the most recent query or connection attempt succeeded. Optionally add a cheap periodic check (`SELECT 1`) when there is little traffic.
- **Probe type:** use the framework's own health endpoint where there is one, such as FastStream's `make_ping_asgi`. Pods without an HTTP server can use an exec probe that reads a status file the app writes.

## Considered options

**Crash when a dependency is unavailable, and let Kubernetes restart the pod.** This is simpler, and restarting does clear a client stuck in a bad state. We rejected it for two reasons. First, restart backoff grows to 5 minutes, which delays recovery once the dependency is back. Second, an outage of one shared dependency puts every pod that uses it into `CrashLoopBackOff`, which hides the pod that is actually broken.

**Check dependencies in the liveness probe.** We rejected this for the same reasons, and because it goes against the Kubernetes guidance for liveness probes. A liveness probe that checks a shared dependency restarts every pod that uses it, and the restarts fix nothing.

**Restart a pod after 15 minutes not ready**, through the app exiting by itself or a liveness probe with a long `failureThreshold`, as a safety net for failures the pod cannot detect itself. We adopted this at first and dropped it. It is still a liveness check on a dependency, only slower: a long outage restarts every pod that uses the dependency once every 15 minutes, a pod that buffers data loses its buffer, and a gateway switched off for maintenance restarts its pod for as long as it is off. The failure it was meant to catch, a client that stops reconnecting without an error, is better caught where it happens: the app exits, or a liveness probe checks that client.

## Out of scope

Buffering or replaying data during an outage, and which alert fires for a not-ready pod, are separate decisions.
