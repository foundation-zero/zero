# THRS Monitoring asks for history by name, and the server shapes it for the chart

The Monitoring page asks for a metric or signal from a fixed list (`MonitoringMetric`, `MonitoringSignal`) over a time range. It never sends table names or SQL. The server maps each name to its table and aggregate in `thrs/monitoring/sources.py`. It returns data the chart draws as it is: series binned to at most 400 points, states merged into segments, and limits as change points.

This keeps the boat's database layout out of the UI and stops any page from running arbitrary queries. Binning in GreptimeDB also keeps a 7-day range small enough for the satellite link. The cost: every new chart starts with a new entry in `sources.py`.

## Considered options

- **Let the client send the query, as Grafana does.** The most flexible option, but the UI would depend on the table layout, and anyone could query the boat's database.
- **Return raw samples and bin in the browser.** A simpler server, but a 7-day range is millions of rows.
