{#
  Greptime stores views as encoded logical plans and cannot rename a view, so
  dbt-postgres's stock `view` materialization — which builds a `__dbt_tmp` view and then
  `ALTER ... RENAME`s it onto the target — fails. Greptime's own re-bind mechanism is
  `CREATE OR REPLACE VIEW`, which is idempotent and rebinds the view to the current schema
  after drift. The two macros below map dbt's `view` materialization onto it.

  See docs/viability-check.md for the full spike findings.
#}

{% macro postgres__create_view_as(relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}
  {{ sql_header if sql_header is not none }}
  create or replace view {{ relation.render() }} as (
    {{ sql }}
  );
{%- endmacro %}


{%- materialization view, adapter='postgres' -%}
  {%- set target_relation = this.incorporate(type='view') -%}
  {%- set grant_config = config.get('grants') -%}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {% call statement('main') -%}
    {{ get_create_view_as_sql(target_relation, sql) }}
  {%- endcall %}

  {% set should_revoke = should_revoke(target_relation, full_refresh_mode=True) %}
  {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}
  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}
  {{ adapter.commit() }}
  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {{ return({'relations': [target_relation]}) }}
{%- endmaterialization -%}
