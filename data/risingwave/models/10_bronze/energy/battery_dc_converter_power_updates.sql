{{ config(materialized='materialized_view') }}

WITH battery_dc_converter_data AS (
    SELECT * FROM {{ ref('battery_dc_converter') }}
)

{{ filter_marpower_topic_changes(
    'battery_dc_converter_data', {
        'Voltage_A' : ('voltage_a', 'voltage_a_timestamp'),
        'Voltage_B' : ('voltage_b', 'voltage_b_timestamp'),
        'Current_A' : ('current_a', 'current_a_timestamp'),
        'Current_B' : ('current_b', 'current_b_timestamp')
    })
}}
