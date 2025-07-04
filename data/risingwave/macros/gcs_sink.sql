{% macro gcs_sink(layer, table, sink_name) %}{{ config(materialized='sink') }}CREATE SINK "{{ sink_name }}" AS
SELECT * FROM "{{ table }}"
WITH (
    connector               = 'gcs',
    gcs.path                = '{{layer }}/{{ table }}',
    gcs.bucket_name         = '{{ env_var('GCS_BUCKET_NAME') }}',
    gcs.credential          = '{{ env_var('GCS_CREDENTIAL') }}',
    type                    = 'append-only',
    max_row_count           = '1000',
    rollover_seconds        = '10',
    path_partition_prefix   = 'hour'
) FORMAT PLAIN ENCODE PARQUET(force_append_only=true);
{% endmacro %}
