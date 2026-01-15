{{ config(materialized='materialized_view') }}

{{ filter_marpower_topic_changes(
    ref('bms_master'), {
        'Stored_Energy' : ('stored_energy', 'stored_energy_timestamp')
    })
}}
