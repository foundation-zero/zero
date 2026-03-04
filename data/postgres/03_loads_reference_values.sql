-- Maximum working loads
INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    v.variable_id,
    load_cases.id,
    v.alarm_low,
    NULL,
    NULL,
    NULL,
    v.alarm_high
FROM (VALUES
    -- MAIN MAST
    ('main-runner-ps-load', NULL, 26.4),
    ('main-runner-sb-load', NULL, 26.4),
    ('main-checkstay-ps-load', NULL, 13.8),
    ('main-checkstay-sb-load', NULL, 13.8),
    ('main-checkstay-deflector-load', NULL, 6.9),
    -- TODO: comb headstay load, fiber optics

    -- MAIN SAIL
    ('main-sheet-load', NULL, 15.0),
    ('main-vang-load', NULL, 61.0),
    ('main-cunningham-load', NULL, 8.6),
    ('main-outhaul-load', NULL, 22.0),
    ('main-preventer-load', NULL, 21.0),

    -- MIZZEN MAST
    ('mizzen-runner-ps-load', NULL, 11.5),
    ('mizzen-runner-sb-load', NULL, 11.5),
    ('mizzen-checkstay-ps-load', NULL, 2.45),
    ('mizzen-checkstay-sb-load', NULL, 2.45),
    ('mizzen-checkstay-deflector-load', NULL, 0.75),
    -- TODO: fiber optics

    -- MIZZEN SAIL
    ('mizzen-sheet-load', NULL, 8.0),
    ('mizzen-vang-load', -22.0, 33.0),
    ('mizzen-cunningham-load', NULL, 6.1),
    ('mizzen-outhaul-load', NULL, 15.4),
    ('mizzen-preventer-load', NULL, 13.9),
    
    -- BLADE
    -- TODO: RT adjuster, cunningham
    ('blade-sheet-feeder-ps-load', NULL, 18.0),
    ('blade-tweaker-ps-load', NULL, 13.8),
    ('blade-sheet-feeder-sb-load', NULL, 18.0),
    ('blade-tweaker-sb-load', NULL, 13.8),

    -- STAYSAIL
    -- RT adjuster
    ('staysail-sheet-feeder-ps-load', NULL, 15.0),
    ('staysail-sheet-feeder-sb-load', NULL, 15.0),

    -- CODE 0
    ('code-zero-tack-load', NULL, 30.0),
    -- sheets loads on primary winches, defined sail-specific below

    -- MIZZEN HEADSAIL
    ('mizzen-headsail-tack-adjuster-load', NULL, 20.0),
    -- sheets loads on aft winches, defined sail-specific below

    --STORM JIB
    ('storm-jib-tack-load', NULL, 27.0)
    -- sheets loads on primary winches, defined sail-specific below
) AS v(variable_id, alarm_low, alarm_high)
CROSS JOIN loads.load_cases;

-- Winch max loads for specific sails 

-- CODE ZERO
INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    v.variable_id,
    load_cases.id,
    NULL,
    NULL,
    NULL,
    NULL,
    v.alarm_high
FROM (VALUES
    ('primary-winch-ps-load', 12.0),
    ('primary-winch-sb-load', 12.0)
) AS v(variable_id, alarm_high)
CROSS JOIN loads.load_cases
JOIN loads.sail_sets AS sail_set ON load_cases.sail_set_id = sail_set.sail_set_id
WHERE sail_set.sail_id = 'code-zero';

-- MIZZEN HEADSAIL
INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    v.variable_id,
    load_cases.id,
    NULL,
    NULL,
    NULL,
    NULL,
    v.alarm_high
FROM (VALUES
    ('aft-winch-ps-load', 9.0),
    ('aft-winch-sb-load', 9.0)
) AS v(variable_id, alarm_high)
CROSS JOIN loads.load_cases
JOIN loads.sail_sets AS sail_set ON load_cases.sail_set_id = sail_set.sail_set_id
WHERE sail_set.sail_id = 'mizzen-jib';

-- STORM JIB
INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    v.variable_id,
    load_cases.id,
    NULL,
    NULL,
    NULL,
    NULL,
    v.alarm_high
FROM (VALUES
    ('primary-winch-ps-load', 13.3),
    ('primary-winch-sb-load', 13.3)
) AS v(variable_id, alarm_high)
CROSS JOIN loads.load_cases
JOIN loads.sail_sets AS sail_set ON load_cases.sail_set_id = sail_set.sail_set_id
WHERE sail_set.sail_id = 'storm-jib';

-- Reference values for specific load cases



-- -- Example reference value for a specific load cases
-- INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
-- SELECT
--     v.variable_id,
--     load_cases.id,
--     v.alarm_low,
--     v.warning_low,
--     v.target,
--     v.warning_high,
--     v.alarm_high
-- FROM (VALUES
--     ('main-runner-ps-load',      6.0, 9.0, 12.0, 15.0, 18.0),
--     ('main-runner-sb-load',      6.0, 9.0, 12.0, 15.0, 18.0),
--     ('main-checkstay-ps-load', 1.0, 3.0, 5.0, 7.0,  9.0),
--     ('main-checkstay-sb-load', 1.0, 3.0, 5.0, 7.0,  9.0),
--     ('main-checkstay-deflector-load', 1.0, 2.0, 4.0, 6.0,  8.0),
--     ('main-checkstay-deflector-relative-position', NULL, NULL, .5, NULL,  NULL)
-- ) AS v(variable_id, alarm_low, warning_low, target, warning_high, alarm_high)
-- CROSS JOIN loads.load_cases
-- JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
-- JOIN loads.sail_sets_combined AS sail_set ON load_cases.sail_set_id = sail_set.id
-- WHERE awa_range.id = 'upwind'
-- AND sail_set.sails = ARRAY['blade', 'full-main', 'full-mizzen'];


-- INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
-- SELECT
--     v.variable_id,
--     load_cases.id,
--     v.alarm_low,
--     v.warning_low,
--     v.target,
--     v.warning_high,
--     v.alarm_high
-- FROM (VALUES
--     ('main-runner-ps-load',      5.0, 9.0, 10.0, 11.0, 20.0),
--     ('main-runner-sb-load',      5.0, 9.0, 10.0, 11.0, 20.0),
--     ('main-checkstay-ps-load', 1.0, 4.0, 7.0, 10.0,  15.0),
--     ('main-checkstay-sb-load', 1.0, 4.0, 7.0, 10.0,  15.0),
--     ('main-checkstay-deflector-load', 1.0, 2.0, 4.0, 6.0,  8.0),
--     ('main-checkstay-deflector-relative-position', NULL, NULL, .8, NULL,  NULL)
-- ) AS v(variable_id, alarm_low, warning_low, target, warning_high, alarm_high)
-- CROSS JOIN loads.load_cases
-- JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
-- JOIN loads.sail_sets_combined AS sail_set ON load_cases.sail_set_id = sail_set.id
-- WHERE awa_range.id = 'reaching'
-- AND sail_set.sails = ARRAY['blade', 'full-main', 'full-mizzen'];


-- INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
-- SELECT
--     'main-vang-load',
--     load_cases.id,
--     NULL,
--     NULL,
--     NULL,
--     NULL,
--     15.0
-- FROM loads.load_cases
-- JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
-- JOIN loads.aws_ranges AS aws_range ON load_cases.aws_range_id = aws_range.id
-- JOIN loads.sail_sets_combined AS sail_set ON load_cases.sail_set_id = sail_set.id
-- WHERE awa_range.id = 'downwind' AND aws_range.aws_range = '[15,20)'::numrange
-- AND sail_set.sails = ARRAY['blade', 'full-main', 'full-mizzen'];


-- INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
-- SELECT
--     'main-traveler-relative-position',
--     load_cases.id,
--     NULL,
--     NULL,
--     .5,
--     NULL,
--     .8
-- FROM loads.load_cases
-- JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
-- WHERE awa_range.id = 'upwind';
