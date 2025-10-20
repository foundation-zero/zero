{% macro sink_upsert_pg(table, key, database, schema) %}WITH (
  connector = 'jdbc',
  jdbc.url = 'jdbc:postgresql://{{ env_var('PG_HOST_DOCKER') }}:{{ env_var('PG_PORT') }}/{{ database }}?user={{ env_var('PG_USER') }}&password={{ env_var('PG_PASSWORD') }}',
  table.name = '{{ table }}',
  schema.name = '{{ schema }}',
  type = 'upsert',
  primary_key = '{{ key }}'
);
{% endmacro %}


