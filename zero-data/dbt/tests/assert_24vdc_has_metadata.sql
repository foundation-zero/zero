/*
 * This test asserts that all 24V DC System devices have corresponding metadata records.
 */

{% set query %}
    with dc_24v_data as (
        select topic
        from {{ ref('stg_marpower__24vdc') }}
        where (output_current__value is not null OR voltage__value is not null)
        order by ts
        limit 10000
    )

    select distinct dc.topic
    from dc_24v_data as dc
    left join {{ source('metadata', 'dc_24v_metadata') }} as meta
        on dc.topic = meta.topic
    where meta.converter is null
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
Missing 24V DC System topics in metadata:
{%- for topic in missing_topics %}
  -> {{ topic }}
{%- endfor %}
==================================================
        {% endset %}
        
        {{ exceptions.raise_compiler_error(error_msg) }}
    {% endif %}
{% endif %}

{{ query }}
