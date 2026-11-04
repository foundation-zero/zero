# Mutations confirm through the State topic

A mutation on a Receive Topic that has a State topic does not return as soon as it publishes. It waits until the State topic shows every value the client supplied, then returns that State value. The input is partial: omitted fields are filled from the State topic's cached value before publishing. A Receive Topic without a State topic returns `Boolean!` once the broker accepts the publish. This lets a client know whether the service actually took the value, not only whether the broker received it, and lets it change one setpoint without restating the whole payload.

## Considered Options

- **Fire-and-forget (`Boolean!` on broker acceptance) everywhere**: simple and needs no pairing, but the client never learns whether the service applied, clamped or ignored the input, and must send full payloads.
- **Echo the published payload**: confirms nothing beyond what the client already knows.
- **Wait for the first State topic update**: services that publish their state periodically can report the old state before handling the input, so the first update proves nothing.
- **Wait for a State value that matches the client-supplied leaves (chosen)**: confirms the effect. Merged-in fields are not compared, because another writer or the service may have changed them in the meantime. A State that already shows the input confirms at once, so setting a value that is already set succeeds even against a service that only publishes on change.

## Consequences

- A Receive Topic is paired with the Send Topic at the same GraphQL path, with no other check. The Specs may be wrong about which Topics have state (for example, `thrs-control` declares no `automation-mode` Send operations). The fix belongs in the Spec, not in bridge heuristics.
- Values are compared by exact JSON equality, so a service that rounds or clamps the input makes the mutation fail. On timeout the mutation returns a plain error after the input has already been published, and the error message is the only sign that the value wasn't confirmed.
- The bridge never writes to the cache. Mutations are off unless enabled in config, because the bridge has no authorization and these inputs actuate equipment.
