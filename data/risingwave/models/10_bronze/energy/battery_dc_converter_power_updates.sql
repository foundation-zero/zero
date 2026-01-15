{{ config(materialized='materialized_view') }}

{{ filter_marpower_topic_changes(
    ref('battery_dc_converter'), {
        'Voltage_A' : ('voltage_a', 'voltage_a_timestamp'),
        'Voltage_B' : ('voltage_b', 'voltage_b_timestamp'),
        'Current_A' : ('current_a', 'current_a_timestamp'),
        'Current_B' : ('current_b', 'current_b_timestamp')
    })
}}
