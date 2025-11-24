{{ config(materialized='materialized_view') }}

-- This temporarily uses dummy data for testing and visualization purposes. This model will be updated to process data from the silver layer.
 SELECT * FROM {{ ref('electrical_soc_dummy_data')}}
