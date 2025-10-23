{% macro only_changes(table, key, value, time) -%}
SELECT
    * EXCEPT (prev_value)
FROM (
    SELECT
        *,
        LAG({{ value }}) OVER (PARTITION BY {{ key }} ORDER BY {{ time }}) AS prev_value
    FROM {{ ref(table) }}
)
WHERE prev_value IS NULL OR {{ value }} <> prev_value
{%- endmacro %}
