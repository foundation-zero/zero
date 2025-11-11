{{ config(materialized='materialized_view') }}

-- For now dummy data is loaded in the materialized view. This will be replace by actual measured data.
SELECT * FROM (
    VALUES
    ('a', ('2025-11-11')::date, 91.3),
    ('b', ('2025-11-11')::date, 141.6)
) AS data(topic, day, soc)
