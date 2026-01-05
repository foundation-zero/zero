{{ config(materialized='materialized_view') }}

SELECT
    time,
    'e1' AS system_code,
    "GEN_SERVICE_14E1_VOLTAGE" AS "voltage"
FROM {{ ref('450000_24vdc_system_general')}}
UNION ALL
SELECT
    time,
    'e2' AS system_code,
    "EMERG_14E2_VOLTAGE" AS "voltage"
FROM {{ ref('450000_24vdc_system_general')}}
UNION ALL 
SELECT
    time,
    'e3' AS system_code,
    "GMDSS_14E3_VOLTAGE" AS "voltage"
FROM {{ ref('450000_24vdc_system_general')}}
