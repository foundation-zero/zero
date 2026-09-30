{{ config(
    materialized='view',
    pre_hook="{{ load_power_tag_metadata() }}"
) }}

select * from power_tag_metadata
