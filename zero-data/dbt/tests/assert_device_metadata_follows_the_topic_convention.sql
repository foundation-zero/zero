/*
 * Every topic is on the convention, and no two kinds share a table. Vector drops the code from the
 * table name, so a system name under two codes would share its tables. A topic with two levels after
 * the system (<kind>/<instance>) and one with one level (a single device, or the system's general
 * topic) get their table from the same level, so a kind cannot also be a single device's name or
 * `general` within one system.
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
),

kinds_with_two_shapes as (
    select "system" || '/' || kind as topic
    from {{ source('metadata', 'marpower__device_metadata') }}
    group by "system", kind
    having count(distinct length(topic) - length(replace(topic, '/', ''))) > 1
)

select topic from off_convention
union all
select topic from systems_under_two_codes
union all
select topic from kinds_with_two_shapes
