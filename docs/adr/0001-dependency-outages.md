# Apps stay up through dependency outages; probes follow Kubernetes

## Context

Our apps depend on shared services: the MQTT broker, databases, Modbus gateways. When RabbitMQ went down during the 2026-10-13 cutover, some apps crash-looped, one stayed `Running` while silently disconnected, and nothing told a person. Restarting an app does not bring a dependency back, and when a shared dependency fails, every pod that uses it turns red, which hides the one that is actually broken.

## Decision

We use each Kubernetes probe for the one question it is meant to answer:

| Probe     | Question                                | May check dependencies? |
| --------- | --------------------------------------- | ----------------------- |
| Liveness  | Would restarting this container fix it? | Never                   |
| Readiness | Can this pod do its job right now?      | Required ones only      |
| Startup   | Has it finished booting?                | No                      |

And for the app itself:

1. **Stay up and retry.** A dependency outage is not a reason to exit. Retry with capped backoff for as long as it lasts.
2. **Start without your dependencies.** Come up, answer probes, and connect in the background.
3. **Exit only when retrying is pointless:** the client has given up, or the configuration is wrong. A refusal such as bad credentials counts as wrong configuration only once it persists past a few retries, since a booting broker can refuse logins too. Say why on the way out.
4. **Each app decides which dependencies are required.** A required dependency is one without which the app cannot do its job. Only required dependencies affect readiness; an optional one is logged and retried.
5. **Log when a dependency goes away and when it comes back.**
6. **A long outage is for people, not restarts.** An alert on pods that stay not ready tells someone to look.

## Consequences

- During an outage, pods show `0/1 Running` instead of restarting, and recover by themselves soon after the dependency is back. k9s shows `0/1 Running` in the same red as `CrashLoopBackOff`.
- A rollout stalls while a required dependency is down, and resumes when it is back.
- Most apps need no liveness probe. Kubernetes does not catch a client that hangs without exiting; we fix that in the client, or give that one app a liveness probe on its own client.

## Considered options

- **Crash and let Kubernetes restart the pod.** Simpler, but restart backoff grows to 5 minutes and delays recovery, and a shared outage puts every pod into `CrashLoopBackOff`.
- **Liveness probes that check a dependency, even with a long threshold** (such as a restart after 15 minutes not ready). A restart does not fix a dependency. It throws away in-memory state such as buffered readings, and it restarts every pod that uses the dependency at once.
