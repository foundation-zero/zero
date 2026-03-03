{{ config(materialized='materialized_view') }}

WITH voltage_data AS (
    SELECT * FROM {{ ref('450000_24vdc_system_general')}}
)

{{ filter_marpower_topic_changes(
    'voltage_data', {
        'GEN_SERVICE_14E1_VOLTAGE' : ('e1_voltage', 'e1_voltage_timestamp'),
        'EMERG_14E2_VOLTAGE' : ('e2_voltage', 'e2_voltage_timestamp'),
        'GMDSS_14E3_VOLTAGE' : ('e3_voltage', 'e3_voltage_timestamp')
    })
}}
