{% macro sink_upsert_pg(table, key) %}WITH (
  connector = 'jdbc',
  jdbc.url = 'jdbc:postgresql://{{ env_var('PG_HOST') }}:{{ env_var('PG_PORT') }}/{{ env_var('PG_DB_DMC') }}?user={{ env_var('PG_USER') }}&password={{ env_var('PG_PASSWORD') }}',
  table.name = '{{ table }}',
  type = 'upsert',
  primary_key = '{{ key }}'
);
{% endmacro %}


