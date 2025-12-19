{{ config(materialized='materialized_view') }}

WITH consumers AS (
    SELECT
        topic,
        time,
        current,
        voltage 
    FROM (
        SELECT
            consumer.topic,
            consumer.time,
            consumer."OutputCurrent" AS current,
            sys_voltage.voltage as voltage,
            row_number() OVER (PARTITION BY consumer.topic, consumer.time ORDER BY sys_voltage.time DESC) AS rn
        FROM {{ ref('450000_24vdc_system')}} consumer
        JOIN {{ ref('24v_system_voltages')}} sys_voltage
            ON sys_voltage.system_code = regexp_match(topic, '/24(e.*)_')[1]
            AND sys_voltage.time BETWEEN consumer.time - INTERVAL '1 minute' AND consumer.time + INTERVAL '1 second'
        ORDER BY consumer.topic, consumer.time, sys_voltage.time
        )
    WHERE rn = 1
    )

{{ filter_marpower_topic_changes(
    'consumers', {
        'current' : ('current', 'curr_timestamp'),
        'voltage' : ('voltage', 'volt_timestamp'),
    })
}}
