/*
 * Every topic is on the convention, and no system name occurs under two codes: Vector drops the code
 * from the table name, so two such systems would share their tables.
 */

with off_convention as (
    select topic
    from {{ source('metadata', 'marpower__device_metadata') }}
    where topic !~ '^marpower/[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*/[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)?$'
),

systems_under_two_codes as (
    select substr("system", 4) as topic
    from {{ source('metadata', 'marpower__device_metadata') }}
    group by substr("system", 4)
    having count(distinct "system") > 1
)

select topic from off_convention
union all
select topic from systems_under_two_codes
