{#
  Greptime only resolves three-part names as "greptime"."<db>"."<table>", but dbt-postgres
  puts the connection's dbname (`public`) in front. Render refs and sources as
  "<db>"."<table>" instead. Any macro that renders a relation itself must do the same with
  `relation.include(database=False)`.
#}
{% macro ref() -%}
  {{ return(builtins.ref(*varargs, **kwargs).include(database=False)) }}
{%- endmacro %}

{% macro source() -%}
  {{ return(builtins.source(*varargs, **kwargs).include(database=False)) }}
{%- endmacro %}
