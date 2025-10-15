{{ config(materialized='materialized_view') }}
{{ get_power_updates('battery_dc_converter', ['Voltage_A', 'Voltage_B', 'Current_A', 'Current_B']) }}
