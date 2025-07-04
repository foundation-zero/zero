{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	GEN_SERVICE_PUMP2_FLD_AVAIL_FDBCK	BOOLEAN,
	GEN_SERVICE_PUMP2_FLD_FAULT_FDBCK	BOOLEAN,
	GEN_SERVICE_PUMP2_FLD_RUN_FDBCK	BOOLEAN,
)
{{ mqtt_with('marpower/210000_general_service') }}
