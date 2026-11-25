-- Both sides of each ESI shore power converter module, in W: the AC power it draws from shore and the DC
-- power it delivers to the 700 VDC bus (battery-side current × voltage), with its running state.
--
-- The DC current reads an offset while a module is idle (AC = 0), measured on 14–24 Nov 2026:
-- 07-11-tbc1a −0.07 A, 07-11-tbc1b −0.11 A, 07-12-tbc1a +1.8 A (≈ +1.2 kW into the bus), 07-12-tbc1b −0.55 A.
-- An idle converter can't deliver power, so these are sensor offsets, not standby draw; the gold views count
-- a module only while it runs. The offset likely stays while a module runs: 07-12-tbc1a then reads about
-- 1.2 kW too much DC, and its loss about as much too little (efficiency 91 % against 89 % for 07-11-tbc1a).
select
    ts,
    topic,
    technical_name                                          as module,
    case
        when technical_name like '07-11-%' then 'Shore power converter PS'
        when technical_name like '07-12-%' then 'Shore power converter SB'
    end                                                     as converter,
    running__value                                          as running,
    -- TODO: The ESI source reports kW; it should report W. Once the source is changed
    -- to W, remove this conversion (* 1000).
    esi_ac_bus_active_power_3_phase__value * 1000           as ac_power,
    esi_battery_current__value * esi_battery_voltage__value as dc_power
from {{ ref('stg_marpower__esi') }}
where technical_name in ('07-11-tbc1a', '07-11-tbc1b', '07-12-tbc1a', '07-12-tbc1b')
and esi_ac_bus_active_power_3_phase__has_value is true
and esi_ac_bus_active_power_3_phase__is_valid is true
and esi_ac_bus_active_power_3_phase__value is not null
and esi_battery_current__has_value is true
and esi_battery_current__is_valid is true
and esi_battery_current__value is not null
and esi_battery_voltage__has_value is true
and esi_battery_voltage__is_valid is true
and esi_battery_voltage__value is not null
and running__has_value is true
and running__is_valid is true
and running__value is not null
