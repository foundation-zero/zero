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
    ('main-headstay-combined-load', NULL, NULL),
    ('fiber-optic-main-v1-ps', NULL, 77.5),
    ('fiber-optic-main-v1-sb', NULL, 77.5),
    ('fiber-optic-main-d1-ps', NULL, 38.8),
    ('fiber-optic-main-d1-sb', NULL, 38.8),

    -- MAIN SAIL
    ('main-sheet-load', NULL, 15.0),
    ('main-vang-load', -29.0, 61.0),
    ('main-cunningham-load', NULL, 8.6),
    ('main-outhaul-load', NULL, 22.0),
    ('main-preventer-load', NULL, 21.0),

    -- MIZZEN MAST
    ('mizzen-runner-ps-load', NULL, 11.5),
    ('mizzen-runner-sb-load', NULL, 11.5),
    ('mizzen-checkstay-ps-load', NULL, 2.45),
    ('mizzen-checkstay-sb-load', NULL, 2.45),
    ('mizzen-checkstay-deflector-load', NULL, 0.75),
    ('fiber-optic-mizzen-v1-ps', NULL, 43.1),
    ('fiber-optic-mizzen-v1-sb', NULL, 43.1),
    ('fiber-optic-mizzen-d1-ps', NULL, 22.8),
    ('fiber-optic-mizzen-d1-sb', NULL, 22.8),
    ('fiber-optic-mizzen-forestay', NULL, 28.5),

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

    -- CODE ZERO
    ('code-zero-tack-load', NULL, 30.0),
    -- sheets loads on primary winches, defined sail-specific below

    -- MIZZEN HEADSAIL
    ('mizzen-headsail-tack-adjuster-load', NULL, 20.0),
    -- sheets loads on aft winches, defined sail-specific below

    -- STORM JIB
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
WHERE sail_set.sail_id = 'code-zero'
-- exclude unrealistic case where code zero and storm jib are both up (they use the same winches)
AND sail_set.sail_set_id NOT IN (
    SELECT sail_sets_2.sail_set_id FROM loads.sail_sets AS sail_sets_2
    WHERE sail_sets_2.sail_id = 'storm-jib'
);

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
WHERE sail_set.sail_id = 'storm-jib'
-- exclude unrealistic case where code zero and storm jib are both up (they use the same winches)
AND sail_set.sail_set_id NOT IN (
    SELECT sail_sets_2.sail_set_id FROM loads.sail_sets AS sail_sets_2
    WHERE sail_sets_2.sail_id = 'code-zero'
);


-- Set warning_high to 90% of alarm_high for all load cases
UPDATE loads.reference_values
SET warning_high = alarm_high * 0.9
WHERE alarm_high IS NOT NULL;

-- Reference values for specific load cases

INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    v.variable_id,
    load_cases.id,
    NULL,
    NULL,
    v.target,
    NULL,
    NULL
FROM (VALUES
    -- MAIN MAST
    ('main-runner-ps-load', 17.3),
    ('main-runner-sb-load', 17.3),
    ('main-checkstay-ps-load', 1.3),
    ('main-checkstay-sb-load', 1.3),
    ('main-checkstay-deflector-load', 0.2),
    ('main-headstay-combined-load', 44.2),
    ('fiber-optic-main-v1-ps', 64.6),
    ('fiber-optic-main-v1-sb', 64.6),
    ('fiber-optic-main-d1-ps', 27.2),
    ('fiber-optic-main-d1-sb', 27.2),

    -- MAIN SAIL
    ('main-sheet-load', 9.6),
    ('main-traveller-relative-position', 0.0),
    ('main-vang-load', 0.1),
    ('main-vang-relative-position', 0.0),
    ('main-cunningham-load', 2.5),
    ('main-outhaul-load', 8.1),
    ('main-preventer-load', 0.0),

    -- MIZZEN MAST
    ('mizzen-runner-ps-load', 0.2),
    ('mizzen-runner-sb-load', 0.2),
    ('mizzen-checkstay-ps-load', 0.3),
    ('mizzen-checkstay-sb-load', 0.3),
    ('mizzen-checkstay-deflector-load', 0.1),
    ('fiber-optic-mizzen-v1-ps', 35.9),
    ('fiber-optic-mizzen-v1-sb', 35.9),
    ('fiber-optic-mizzen-d1-ps', 14.8),
    ('fiber-optic-mizzen-d1-sb', 14.8),
    ('fiber-optic-mizzen-forestay', 24.5),

    -- MIZZEN SAIL
    ('mizzen-sheet-load', 6.8),
    ('mizzen-vang-load', 0.0),
    ('mizzen-cunningham-load', 1.5),
    ('mizzen-outhaul-load', 7.1),
    ('mizzen-outhaul-relative-position', 0.04),
    ('mizzen-preventer-load', 0.0),
    
    -- BLADE
    -- TODO: RT adjuster, cunningham
    ('blade-sheet-feeder-ps-load', 9.8),
    ('blade-tweaker-ps-load', 4.4),
    ('blade-sheet-feeder-sb-load', 9.8),
    ('blade-tweaker-sb-load', 4.4)
) AS v(variable_id, target)
CROSS JOIN loads.load_cases
JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
JOIN loads.aws_ranges AS aws_range ON load_cases.aws_range_id = aws_range.id
JOIN loads.sail_sets_combined AS sail_set ON load_cases.sail_set_id = sail_set.id
WHERE awa_range.id = 'upwind'
AND aws_range.aws_range = '[20,25)'::numrange
AND sail_set.sails = ARRAY['blade', 'full-main', 'full-mizzen']
ON CONFLICT (load_case_id, variable_id) DO UPDATE
    SET target = EXCLUDED.target;
