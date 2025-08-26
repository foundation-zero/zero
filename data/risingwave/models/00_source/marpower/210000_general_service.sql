{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"GEN_SERVICE_PUMP2_FLD_AVAIL_FDBCK"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERVICE_PUMP2_FLD_FAULT_FDBCK"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERVICE_PUMP2_FLD_RUN_FDBCK"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/210000-general-service') }}
