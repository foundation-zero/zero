# zero-health

Serves `/health/ready` and `/health/alive` for a service, following
[ADR 0001](../../../docs/adr/0001-dependency-outages.md).

```python
async def mqtt() -> str | None:
    return None if await broker.ping(timeout=5) else "ping failed"

health = Health(HealthSettings(), {"mqtt": mqtt})
async with health.serve():
    await app.run()
```

A check is an async function that returns `None` while its dependency is
usable, or the reason it is not. Every `HEALTH_CHECK_INTERVAL` seconds the
service runs all checks, each limited to `HEALTH_CHECK_TIMEOUT` seconds, and
logs every change. The endpoints answer from the last results, so a probe
never waits on a dependency.

- `GET /health/ready`: `204`, or `500` with one line per failing check, such
  as `mqtt: ping failed (not connected)`.
- `GET /health/alive`: always `204`. It is served on the service's event loop,
  so the probe times out when that loop is blocked, and it never depends on a
  dependency.

Not ready for `HEALTH_DEADLINE_SECONDS` (900, must be over 600) exits the process
with the failing checks as the termination message.

| Variable | Default |
|---|---|
| `HEALTH_PORT` | `8080` |
| `HEALTH_CHECK_INTERVAL` | `10` |
| `HEALTH_CHECK_TIMEOUT` | `5` |
| `HEALTH_DEADLINE_SECONDS` | `900` |

## Development

```sh
just check
```
