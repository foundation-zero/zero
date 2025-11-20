{{ config(materialized='table_with_connector') }}

-- This temporarily table is filled with dummy data which is to enable testing and visualization historical SoC data. This table will be removed soon.
CREATE TABLE {{ this }} AS
SELECT
    topic,
    hour,
    soc_value - 30 * random() * GREATEST(0, date_part('day', hour - (now() - INTERVAL '4 days'))) AS soc
FROM (
    SELECT
        e.entity AS topic,
        g.ts AS hour,
        e.base::numeric * (1 + (random() - 0.5) * 0.8) AS soc_value
    FROM (
    VALUES
        ('a', 100.0),
        ('b', 150.0)
    ) AS e(entity, base)
    CROSS JOIN generate_series(
        date_trunc('hour', now() - interval '60 days')::timestamptz,
        date_trunc('hour', now())::timestamptz,
        interval '1 hour'
    ) AS g(ts)
)
