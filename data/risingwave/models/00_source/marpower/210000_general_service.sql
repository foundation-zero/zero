{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"PUMP2_FLD_AVAILFDBCK"	{{ marpower_struct("BOOLEAN") }},
	"PUMP2_FLD_RUNFDBCK"	{{ marpower_struct("BOOLEAN") }},
	"PUMP2_FLD_FAULTFDBCK"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/210000-general-service') }}
