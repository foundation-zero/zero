{% macro sink_append(table) %}WITH (
  connector = 'jdbc',
  jdbc.url = 'jdbc:postgresql://postgres:{{ env_var('PG_PORT') }}/{{ env_var('PG_DB') }}?user={{ env_var('PG_USER') }}&password={{ env_var('PG_PASSWORD') }}',
  table.name = '{{ table}}',
  force_append_only='true',
  type = 'append-only'
);
{% endmacro %}
