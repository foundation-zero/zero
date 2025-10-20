{{ config(materialized='materialized_view') }}

WITH bms_master AS (
    SELECT * FROM {{ ref('bms_master') }}
)

{{ filter_marpower_topic_changes(
    'bms_master', {
        'Stored_Energy' : ('stored_energy', 'stored_energy_timestamp')
    })
}}
