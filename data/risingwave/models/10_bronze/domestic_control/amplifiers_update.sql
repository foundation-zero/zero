{{ config(materialized='materialized_view') }}
{{ only_changes("amplifiers_update_source", "id", "is_on", "time") }}
