{{ config(materialized='materialized_view') }}

WITH current_data AS (
    SELECT * FROM {{ ref('450000_24vdc_system')}}
)

{{ filter_marpower_topic_changes(
    'current_data', {
        'OutputCurrent' : ('current', 'curr_timestamp')
    })
}}
