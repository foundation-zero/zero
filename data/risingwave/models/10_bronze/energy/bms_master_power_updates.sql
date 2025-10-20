{{ config(materialized='materialized_view') }}

WITH bms_master AS (
    SELECT * FROM {{ ref('bms_master') }}
)


{{ distinct_timestamp(
    'bms_master', {
        'Stored_Power' : ('stored_power', 'stored_power_timestamp'),
        'Stored_Energy' : ('stored_energy', 'stored_energy_timestamp')
    })
}}