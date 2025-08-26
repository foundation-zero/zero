{{ config(materialized='table') }}
SELECT *
FROM postgres_query(
    '{{ env_var('PG_HOST_DOCKER') }}',
    '{{ env_var('PG_PORT') }}',
    '{{ env_var('PG_USER') }}',
    '{{ env_var('PG_PASSWORD') }}',
    '{{ env_var('PG_DB') }}',
    'SELECT * FROM amplifiers;'
);
