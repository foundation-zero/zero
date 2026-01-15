{{ config(materialized='materialized_view') }}

SELECT
    topic,
    MAX(regexp_match(topic, '/24(e\w+)_')[1]) AS system_code
FROM {{ ref('24v_current_updates')}}
GROUP BY topic
