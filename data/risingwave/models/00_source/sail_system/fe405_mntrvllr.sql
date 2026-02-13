{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"relative_position_dummy"	INTEGER
)
{{ mqtt_with('sail-systems/fe405_mntrvllr') }}
