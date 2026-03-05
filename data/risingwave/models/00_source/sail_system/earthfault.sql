{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"i_FPKIsoDC"	INTEGER,
	"i_MAINIsoDC"	INTEGER,
	"i_HYPIsoDC"	INTEGER,
	"i_LAZIsoDC"	INTEGER,
	"x_FPKIsoDC"	BOOLEAN,
	"x_MAINIsoDC"	BOOLEAN,
	"x_HYPIsoDC"	BOOLEAN,
	"x_LAZIsoDC"	BOOLEAN
)
{{ mqtt_with('sail-systems/ef') }}
