/*
 * This test asserts that all active power tags have corresponding metadata records.
 */

{% set query %}
    with power_tag_data as (
        select topic
        from {{ ref('stg_marpower__power_tags') }}
        where active_power_total is not null
        order by ts desc
        limit 10000
    )

    select distinct pt.topic
    from power_tag_data as pt
    left join {{ source('metadata', 'power_tag_metadata') }} as meta
        on pt.topic = meta.topic
    where meta.main_group is null
{% endset %}

{% if execute %}
    {% set results = run_query(query) %}
    {% if results and results.rows %}
        {% set missing_topics = [] %}
        {% for row in results.rows %}
            {% do missing_topics.append(row[0]) %}
        {% endfor %}
        
        {% set error_msg %}
==================================================
Missing power tags topics in metadata:
{%- for topic in missing_topics %}
  -> {{ topic }}
{%- endfor %}
==================================================
        {% endset %}
        
        {{ exceptions.raise_compiler_error(error_msg) }}
    {% endif %}
{% endif %}

{{ query }}
