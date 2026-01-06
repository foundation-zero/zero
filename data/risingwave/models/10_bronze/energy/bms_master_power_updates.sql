{{ config(materialized='materialized_view') }}

WITH bms_master_data AS (
    SELECT * FROM {{ ref('bms_master') }}
)

{{ filter_marpower_topic_changes(
    'bms_master_data', {
        'Stored_Energy' : ('stored_energy', 'stored_energy_timestamp')
    })
}}
