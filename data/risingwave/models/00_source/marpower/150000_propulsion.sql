{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"STARTCOMM"	{{ marpower_struct("BOOLEAN") }},
	"STOPCOMM"	{{ marpower_struct("BOOLEAN") }},
	"RESETCOMM"	{{ marpower_struct("BOOLEAN") }},
	"EMSTOPACT"	{{ marpower_struct("BOOLEAN") }},
	"SECTHRSEL"	{{ marpower_struct("BOOLEAN") }},
	"NAMURFAULT"	{{ marpower_struct("BOOLEAN") }},
	"SHAFTBRAKEENG"	{{ marpower_struct("BOOLEAN") }},
	"DRIVEREADYFDBCK"	{{ marpower_struct("BOOLEAN") }},
	"DRIVERUNNINGFDBCK"	{{ marpower_struct("BOOLEAN") }},
	"DRIVEWARNFDBCK"	{{ marpower_struct("BOOLEAN") }},
	"DRIVEFAILFDBCK"	{{ marpower_struct("BOOLEAN") }},
	"DRIVEPWRREDUCEFDBCK"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/150000-propulsion/#') }}
