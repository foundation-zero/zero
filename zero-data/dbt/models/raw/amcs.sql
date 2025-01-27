{{ config(materialized='view') }}
SELECT
    amcs.timestamp,
    amcs.data,
    amcs.topic,
    meta.data_type
FROM
    {{ ref("amcs_input") }} AS amcs
LEFT JOIN
    {{ ref("io_metadata") }} as meta
ON
    meta.tag = amcs.topic