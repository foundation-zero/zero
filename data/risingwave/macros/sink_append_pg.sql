{% macro sink_append_pg(table, database) %}WITH (
  connector = 'jdbc',
  jdbc.url = 'jdbc:postgresql://{{ env_var('PG_HOST_DOCKER') }}:{{ env_var('PG_PORT') }}/{{ database }}?user={{ env_var('PG_USER') }}&password={{ env_var('PG_PASSWORD') }}',
  table.name = '{{ table}}',
  force_append_only='true',
  type = 'append-only'
);
{% endmacro %}
