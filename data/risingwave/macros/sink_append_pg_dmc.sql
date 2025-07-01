{% macro sink_append_pg(table) %}WITH (
  connector = 'jdbc',
  jdbc.url = 'jdbc:postgresql://{{ env_var('PG_HOST') }}:{{ env_var('PG_PORT') }}/{{ env_var('PG_DB_DMC') }}?user={{ env_var('PG_USER') }}&password={{ env_var('PG_PASSWORD') }}',
  table.name = '{{ table}}',
  force_append_only='true',
  type = 'append-only'
);
{% endmacro %}
