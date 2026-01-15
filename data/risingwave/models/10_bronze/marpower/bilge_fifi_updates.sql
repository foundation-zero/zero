{{ config(materialized='materialized_view') }}

{{ filter_marpower_topic_changes(
    ref('210000_bilge_fifi'), {
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
