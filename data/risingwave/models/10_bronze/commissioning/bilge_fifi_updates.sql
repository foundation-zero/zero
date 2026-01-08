{{ config(materialized='materialized_view') }}

WITH bilge_fifi_data AS (
    SELECT * FROM {{ ref('210000_bilge_fifi') }}
)

{{ filter_marpower_topic_changes(
    'bilge_fifi_data', {
        'Opened' : ('opened', 'opened_timestamp'),
        'Closed' : ('closed', 'closed_timestamp'),
        'HmiCmdOpen' : ('hmi_cmd_open', 'hmi_cmd_open_timestamp'),
        'HmiCmdClose' : ('hmi_cmd_close', 'hmi_cmd_close_timestamp'),
        'ShouldBeOpen' : ('should_be_open', 'should_be_open_timestamp'),
        'HmiControlAvailable' : ('hmi_control_available', 'hmi_control_available_timestamp'),
        'Open' : ('open', 'open_timestamp'),
        'Close' : ('close', 'close_timestamp'),
        'Alarm' : ('alarm', 'alarm_timestamp')
    })
}}
