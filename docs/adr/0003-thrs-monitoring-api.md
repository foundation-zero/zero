---
status: proposed
---

# The THRS Monitoring API runs as its own small service in zero-thrs-control

The Monitoring page needs a small GraphQL API: history from GreptimeDB, plus the crew's notes. That API was built into thrs-api, which [#1099](https://github.com/foundation-zero/zero/pull/1099) removed. We propose a separate `thrs-monitoring` process, run from the zero-thrs-control image with its own Deployment, that serves only this API and never touches MQTT or the control loops. It keeps what the page needs without bringing back the MQTT API that zero-mqtt-graphql replaced.

The history and notes code is in `zero-thrs-control/src/thrs/monitoring/`. Its GraphQL resolvers were written against thrs-api's context, so they are not in this change. They are on the `design-playground` branch (`46d5af06`), in `src/thrs/graphql/monitoring.py`, ready to wire into the new service. Until the service exists, every chart on the page shows "Couldn't load this chart".

## Considered options

- **A history service for all systems, outside zero-thrs-control.** This is the better home once a second system needs history, but today it would mean a new app, chart and CI workflow for one page. `thrs/monitoring` only needs a SQLAlchemy engine, so moving it there later is cheap.
- **Serve history from zero-mqtt-graphql.** The UI already talks to it. But it is a Rust service built around MQTT; history would add a second data source and mean rewriting the binning and state merging in Rust.
- **Bring thrs-api back.** It was removed on purpose, and almost all of it is the MQTT API that has been replaced.
