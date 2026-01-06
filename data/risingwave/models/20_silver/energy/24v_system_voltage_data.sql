{{ config(materialized='materialized_view') }}

    SELECT
        'e1' AS system_code,
        time,
        e1_voltage AS voltage,
        e1_voltage_timestamp AS voltage_timestamp
    FROM {{ ref('24v_system_voltage_updates')}}
    UNION ALL
    SELECT
        'e2' AS system_code,
        time,
        e2_voltage AS voltage,
        e2_voltage_timestamp AS voltage_timestamp
    FROM {{ ref('24v_system_voltage_updates')}}
    UNION ALL 
    SELECT
        'e3' AS system_code,
        time,
        e3_voltage AS voltage,
        e3_voltage_timestamp AS voltage_timestamp
    FROM {{ ref('24v_system_voltage_updates')}}
