{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	BCKUP_GEN_SERV_PUMP_FIELD_RUNN_FDBCK	BOOLEAN,
)
{{ mqtt_with('KEB2_DO60') }}