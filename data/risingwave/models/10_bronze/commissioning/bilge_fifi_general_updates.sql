{{ config(materialized='materialized_view') }}

WITH bilge_fifi_general_data AS (
    SELECT * FROM {{ ref('210000_bilge_fifi_general') }}
)

{{ filter_marpower_topic_changes(
    'bilge_fifi_general_data', {
        'LEVEL_SUB_PUMP1_ALARM' : ('sub_pump1_alarm', 'sub_pump1_alarm_timestamp'),
        'LEVEL_SUB_PUMP2_ALARM' : ('sub_pump2_alarm', 'sub_pump2_alarm_timestamp'),
        'LEVEL_SUB_PUMP3_ALARM' : ('sub_pump3_alarm', 'sub_pump3_alarm_timestamp'),
        'FRAME68_ALARM' : ('frame68_alarm', 'frame68_alarm_timestamp'),
        'FRAME53_ALARM' : ('frame53_alarm', 'frame53_alarm_timestamp'),
        'BATT_COMP_5_ALARM' : ('batt_comp_5_alarm', 'batt_comp_5_alarm_timestamp'),
        'BATT_COMP_6_ALARM' : ('batt_comp_6_alarm', 'batt_comp_6_alarm_timestamp'),
        'FRAME48_ALARM' : ('frame48_alarm', 'frame48_alarm_timestamp'),
        'FRAME46_ALARM' : ('frame46_alarm', 'frame46_alarm_timestamp'),
        'FRAME47SB_ALARM' : ('frame47sb_alarm', 'frame47sb_alarm_timestamp'),
        'FRAME38_ALARM' : ('frame38_alarm', 'frame38_alarm_timestamp'),
        'FRAME30_ALARM' : ('frame30_alarm', 'frame30_alarm_timestamp'),
        'FRAME15_ALARM' : ('frame15_alarm', 'frame15_alarm_timestamp'),
        'FRAME13_ALARM' : ('frame13_alarm', 'frame13_alarm_timestamp'),
        'FRAME38PS_ALARM' : ('frame38ps_alarm', 'frame38ps_alarm_timestamp'),
        'FRAME38SB_ALARM' : ('frame38sb_alarm', 'frame38sb_alarm_timestamp'),
        'GEN_SERV_PUMP1_REMAVAIL' : ('gen_serv_pump1_remavail', 'gen_serv_pump1_remavail_timestamp'),
        'GEN_SERV_PUMP2_REMAVAIL' : ('gen_serv_pump2_remavail', 'gen_serv_pump2_remavail_timestamp'),
        'GEN_SERV_PUMP2_FIELD_START' : ('gen_serv_pump2_field_start', 'gen_serv_pump2_field_start_timestamp'),
        'GEN_SERV_PUMP2_FIELD_STOP' : ('gen_serv_pump2_field_stop', 'gen_serv_pump2_field_stop_timestamp'),
        'STRIP_PUMP_REMAVAIL' : ('strip_pump_remavail', 'strip_pump_remavail_timestamp'),
        'STRIP_PUMP_RUNNING' : ('strip_pump_running', 'strip_pump_running_timestamp'),
        'CHAIN_LOCK_PUMP_REMAVAIL' : ('chain_lock_pump_remavail', 'chain_lock_pump_remavail_timestamp'),
        'CHAIN_LOCK_PUMP_RUNNING' : ('chain_lock_pump_running', 'chain_lock_pump_running_timestamp'),
        'SUBMERS_PUMP1_REMAVAIL' : ('submers_pump1_remavail', 'submers_pump1_remavail_timestamp'),
        'SUBMERS_PUMP1_RUNNING' : ('submers_pump1_running', 'submers_pump1_running_timestamp'),
        'SUBMERS_PUMP2_REMAVAIL' : ('submers_pump2_remavail', 'submers_pump2_remavail_timestamp'),
        'SUBMERS_PUMP2_RUNNING' : ('submers_pump2_running', 'submers_pump2_running_timestamp'),
        'SUBMERS_PUMP3_REMAVAIL' : ('submers_pump3_remavail', 'submers_pump3_remavail_timestamp'),
        'SUBMERS_PUMP3_RUNNING' : ('submers_pump3_running', 'submers_pump3_running_timestamp'),
        'BCKUP_GEN_SERV_PUMP_REMAVAIL' : ('bckup_gen_serv_pump_remavail', 'bckup_gen_serv_pump_remavail_timestamp'),
        'STRIP_PUMP_STARTSTOP' : ('strip_pump_startstop', 'strip_pump_startstop_timestamp'),
        'CHAIN_LOCK_PUMP_STARTSTOP' : ('chain_lock_pump_startstop', 'chain_lock_pump_startstop_timestamp'),
        'GEN_SERV_PUMP1_FDBCK_FAULT' : ('gen_serv_pump1_fdbck_fault', 'gen_serv_pump1_fdbck_fault_timestamp'),
        'SUBMERS_PUMP1_STARTSTOP' : ('submers_pump1_startstop', 'submers_pump1_startstop_timestamp'),
        'SUBMERS_PUMP2_STARTSTOP' : ('submers_pump2_startstop', 'submers_pump2_startstop_timestamp'),
        'SUBMERS_PUMP3_STARTSTOP' : ('submers_pump3_startstop', 'submers_pump3_startstop_timestamp'),
        'SEPARATOR_START' : ('separator_start', 'separator_start_timestamp'),
        'TANK_LEVEL' : ('tank_level', 'tank_level_timestamp'),
        'PRESS_SENSOR_AFT_PS_BATTERY' : ('press_sensor_aft_ps_battery', 'press_sensor_aft_ps_battery_timestamp'),
        'PRESSURE_SENSOR_210010691' : ('pressure_sensor_210010691', 'pressure_sensor_210010691_timestamp'),
        'PRESSURE_SENSOR_210010692' : ('pressure_sensor_210010692', 'pressure_sensor_210010692_timestamp'),
        'PRESSURE_SENSOR_210010693' : ('pressure_sensor_210010693', 'pressure_sensor_210010693_timestamp'),
        'PRESS_SENSOR_AFT_SB_BATTERY' : ('press_sensor_aft_sb_battery', 'press_sensor_aft_sb_battery_timestamp'),
        'CHAIN_LOCK_PRESSSENSOR' : ('chain_lock_presssensor', 'chain_lock_presssensor_timestamp'),
        'PRESS_SENSOR_FWD_PS_BATTERY' : ('press_sensor_fwd_ps_battery', 'press_sensor_fwd_ps_battery_timestamp'),
        'PRESS_SENSOR_FWD_SB_BATTERY' : ('press_sensor_fwd_sb_battery', 'press_sensor_fwd_sb_battery_timestamp'),
        'FOREPEAK_TEMPSENSOR' : ('forepeak_tempsensor', 'forepeak_tempsensor_timestamp')
    })
}}
