/*
 * Metadata of the 700 VDC ring: its DC switches, the measured sources on each bus segment, and the class
 * of each segment's unallocated load. Created by a macro for the same reason as load_24vdc_metadata: a
 * Greptime table needs a time index, which dbt seeds can't give.
 *
 * Ring order, in the direction of a positive flow:
 *   05.71 | SB.01.P01 | 05.72 | SB.01.P02 | 05.73 | SB.01.P03 | 05.74 | SB.01.P04 | 05.75 | cable |
 *   05.76 | SB.02.P01 | 05.77 | SB.02.P02 | 05.78 | cable | 05.71
 *
 * The documents don't say which segment is on section 0 of a switch. The signs are fitted from the data:
 * with them, each segment's load follows its measured sources at a coefficient close to 1 (11 Nov 2026 on
 * the old topics; again on 16–24 Nov on marpower__dc_700v__dc_switch).
 *
 * The placement of the sources comes from the data where a source varies enough to be fitted (shore and
 * grid converters, battery converters 05.41–05.44, 350 VDC converters, thrusters), and from the drawings
 * and functional description v5.0 (9445203-2) otherwise. As built differs from the functional description
 * in one place: grid converter 05.12 is on SB.02.P01, not SB.02.P02.
 */

{% macro load_dc_ring_metadata() %}

    {% set query %}
        DROP TABLE IF EXISTS dc_ring_switch_metadata;

        CREATE TABLE dc_ring_switch_metadata (
            ts TIMESTAMP,
            technical_name STRING,
            sign INT,
            upstream_segment STRING,
            downstream_segment STRING,
            TIME INDEX (ts),
            PRIMARY KEY (technical_name)
        );

        -- The flow from upstream_segment to downstream_segment is sign × the power through the switch.
        INSERT INTO dc_ring_switch_metadata (ts, technical_name, sign, upstream_segment, downstream_segment)
        VALUES
            ('1970-01-01 00:00:00', '05-71-q101',  1, 'Cable SB.02.P02-SB.01.P01', 'SB.01.P01'),
            ('1970-01-01 00:00:00', '05-72-q101', -1, 'SB.01.P01', 'SB.01.P02'),
            ('1970-01-01 00:00:00', '05-73-q101', -1, 'SB.01.P02', 'SB.01.P03'),
            ('1970-01-01 00:00:00', '05-74-q101', -1, 'SB.01.P03', 'SB.01.P04'),
            ('1970-01-01 00:00:00', '05-75-q101', -1, 'SB.01.P04', 'Cable SB.01.P04-SB.02.P01'),
            ('1970-01-01 00:00:00', '05-76-q101', -1, 'Cable SB.01.P04-SB.02.P01', 'SB.02.P01'),
            ('1970-01-01 00:00:00', '05-77-q101', -1, 'SB.02.P01', 'SB.02.P02'),
            ('1970-01-01 00:00:00', '05-78-q101',  1, 'SB.02.P02', 'Cable SB.02.P02-SB.01.P01');

        DROP TABLE IF EXISTS dc_ring_source_metadata;

        CREATE TABLE dc_ring_source_metadata (
            ts TIMESTAMP,
            kind STRING,
            unit STRING,
            segment STRING,
            TIME INDEX (ts),
            PRIMARY KEY (kind, unit)
        );

        -- The measured sources on each segment, with the unit as the source's silver model names it.
        INSERT INTO dc_ring_source_metadata (ts, kind, unit, segment)
        VALUES
            -- Shore power converters, ESI =07.11 and =07.12.
            ('1970-01-01 00:00:00', 'shore_converter', '07-11', 'SB.01.P01'),
            ('1970-01-01 00:00:00', 'shore_converter', '07-12', 'SB.01.P04'),
            -- Battery converters, Brightloop =05.41 to =05.46. 05.45 and 05.46 are offline; their
            -- placement is from the functional description.
            ('1970-01-01 00:00:00', 'battery', '05-41', 'SB.01.P01'),
            ('1970-01-01 00:00:00', 'battery', '05-42', 'SB.01.P02'),
            ('1970-01-01 00:00:00', 'battery', '05-43', 'SB.01.P03'),
            ('1970-01-01 00:00:00', 'battery', '05-44', 'SB.01.P04'),
            ('1970-01-01 00:00:00', 'battery', '05-45', 'SB.02.P01'),
            ('1970-01-01 00:00:00', 'battery', '05-46', 'SB.02.P02'),
            -- Grid converters, uGrid =05.11-U101 and =05.12-U101 (as built, see above).
            ('1970-01-01 00:00:00', 'grid_converter', '05-11-u101', 'SB.01.P04'),
            ('1970-01-01 00:00:00', 'grid_converter', '05-12-u101', 'SB.02.P01'),
            -- 350 VDC converters, aft =02.71 and fwd =02.72.
            ('1970-01-01 00:00:00', 'dc_350v_converter', '02-71-t101', 'SB.01.P04'),
            ('1970-01-01 00:00:00', 'dc_350v_converter', '02-71-t102', 'SB.01.P04'),
            ('1970-01-01 00:00:00', 'dc_350v_converter', '02-72-t101', 'SB.02.P02'),
            ('1970-01-01 00:00:00', 'dc_350v_converter', '02-72-t102', 'SB.02.P02'),
            -- 24 VDC power supplies, per converter group. Their load is too steady to fit. From the
            -- drawings (9445450, 9445452) and the functional description: 14E1 (service) is fed from
            -- SB.01.P02, 14E2 (emergency) from SB.01.P03, and both from SB.02.P01. Which group takes which
            -- feed is assumed: _01 the aft feed, _02 the fwd feed. Their output power is used: the
            -- converter losses stay in the segment remainder.
            ('1970-01-01 00:00:00', 'dc_24v_converter', 'W14E1_01', 'SB.01.P02'),
            ('1970-01-01 00:00:00', 'dc_24v_converter', 'W14E1_02', 'SB.02.P01'),
            ('1970-01-01 00:00:00', 'dc_24v_converter', 'W14E2_01', 'SB.01.P03'),
            ('1970-01-01 00:00:00', 'dc_24v_converter', 'W14E2_02', 'SB.02.P01'),
            -- Thruster drives: the stern drive =13.11 has a winding on SB.01.P01 and one on SB.01.P04, the
            -- bow drive =13.31 one on SB.02.P01 and one on SB.02.P02. The two Aradexes of a drive read
            -- the same, so which one is on which segment doesn't change the result.
            ('1970-01-01 00:00:00', 'aradex', 'AFT-1', 'SB.01.P01'),
            ('1970-01-01 00:00:00', 'aradex', 'AFT-2', 'SB.01.P04'),
            ('1970-01-01 00:00:00', 'aradex', 'FWD-1', 'SB.02.P01'),
            ('1970-01-01 00:00:00', 'aradex', 'FWD-2', 'SB.02.P02'),
            -- Compression chiller =30.11: on 26 Jun 2026, SB.01.P02 followed it at 0.93 kW per kW.
            ('1970-01-01 00:00:00', 'chiller', 'chiller', 'SB.01.P02');

        DROP TABLE IF EXISTS dc_ring_segment_metadata;

        CREATE TABLE dc_ring_segment_metadata (
            ts TIMESTAMP,
            segment STRING,
            main_group STRING,
            sub_group STRING,
            TIME INDEX (ts),
            PRIMARY KEY (segment)
        );

        -- The class of each segment's unallocated load. The cable segments have nothing connected: their
        -- remainder is the measurement error of the switches, not a load, so they have no class.
        -- The domestic water heaters (=25.41) are on SB.01.P03 (4–9 and 18) and SB.02.P02 (10–17). They have
        -- no power signal; once they do, decide between Technical / Fresh water and Domestic / Hot water.
        INSERT INTO dc_ring_segment_metadata (ts, segment, main_group, sub_group)
        VALUES
            ('1970-01-01 00:00:00', 'SB.01.P01', 'Propulsion', 'Thrusters (unallocated)'),
            ('1970-01-01 00:00:00', 'SB.01.P02', 'Technical', '700VDC unallocated'),
            ('1970-01-01 00:00:00', 'SB.01.P03', 'Technical', '700VDC unallocated'),
            ('1970-01-01 00:00:00', 'SB.01.P04', 'Propulsion', 'Thrusters (unallocated)'),
            ('1970-01-01 00:00:00', 'SB.02.P01', 'Technical', '700VDC unallocated'),
            ('1970-01-01 00:00:00', 'SB.02.P02', 'Technical', '700VDC unallocated'),
            ('1970-01-01 00:00:00', 'Cable SB.01.P04-SB.02.P01', NULL, NULL),
            ('1970-01-01 00:00:00', 'Cable SB.02.P02-SB.01.P01', NULL, NULL);
    {% endset %}

    {% do log("Create DC ring metadata tables and insert data...", info=True) %}
    {% do run_query(query) %}
    {% do log("Success! Data has been loaded.", info=True) %}

{% endmacro %}
