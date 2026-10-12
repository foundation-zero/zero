{{ config(
    materialized='view',
    pre_hook="{{ load_24vdc_metadata() }}"
) }}

select * from "dc_24v_metadata"
