{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_Stat_HMI_Keel_lift_Cyl"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Keel_lift_Cyl"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Keel_lift_Cyl_Up_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Keel_lift_Cyl_Down_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Keel_lift_Cyl_up_cycle_time_out_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Keel_lift_Cyl_down_cycle_time_out_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Keel_lift_Cyl_Sensor_failure_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Keel_lock_Cyl"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Keel_lock_Cyl"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Keel_lift_Cyl_Locked_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Keel_lift_Cyl_Unlocked_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Keel_lock_Cyl_lock_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Keel_spare"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Keel_spare"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Keel_lift_Cyl"	{{ marpower_struct("BOOLEAN") }},
	"Button_Keel_lift_Cyl_Up_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Button_Keel_lift_Cyl_Down_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Keel_lock_Cyl"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Keel_spare"	{{ marpower_struct("BOOLEAN") }},
	"Keel_lift_Cyl_Act_Position_Mill"	{{ marpower_struct("INTEGER") }},
	"Keel_lift_Cyl_Act_Position_Perm"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/keel') }}
