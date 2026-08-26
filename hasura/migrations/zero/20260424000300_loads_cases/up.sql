-- Define sail positions
INSERT INTO loads.sail_positions (id) VALUES
  ('main'),
  ('mizzen'),
  ('fore-inner'),
  ('fore-outer'),
  ('mizzen-fore');

-- Define sails
INSERT INTO loads.sails (id, abbreviation, position_id, name, variant_name) VALUES
  ('full-main', 'FM', 'main', 'Full Main', 'Full'),
  ('main-reef1', 'M1R', 'main', 'Main 1 Reef', 'Reef 1'),
  ('main-reef2', 'M2R', 'main', 'Main 2 Reef', 'Reef 2'),
  ('main-reef3', 'M3R', 'main', 'Main 3 Reef', 'Reef 3'),
  ('trisail', 'TS', 'main', 'Trisail', 'Trisail'),
  ('full-mizzen', 'FMZ', 'mizzen', 'Full Mizzen', 'Full'),
  ('mizzen-reef1', 'MZ1R', 'mizzen', 'Mizzen 1 Reef', 'Reef 1'),
  ('mizzen-reef2', 'MZ2R', 'mizzen', 'Mizzen 2 Reef', 'Reef 2'),
  ('utility-main', 'UM', 'main', 'Utility Main', 'Utility'),
  ('blade', 'B', 'fore-outer', 'Blade', 'Blade'),
  ('code-zero', 'C0', 'fore-outer', 'Code Zero', 'Code Zero'),
  ('A3', 'A3', 'fore-outer', 'A3', 'A3'),
  ('A2', 'A2', 'fore-outer', 'A2', 'A2'),
  ('storm-jib', 'SJ', 'fore-inner', 'Storm Jib', 'Storm Jib'),
  ('staysail', 'SS', 'fore-inner', 'Staysail', 'Staysail'),
  ('mizzen-jib', 'MZJ', 'mizzen-fore', 'Mizzen Jib', 'Jib'),
  ('mizzen-staysail', 'MZSS', 'mizzen-fore', 'Staysail', 'Staysail');

-- Generate all possible sail sets based on position (including those with NULLs for missing sails)
WITH RECURSIVE indexed_positions AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY id) AS position_index,
        id AS position
    FROM loads.sail_positions
),
options AS (
    SELECT
        position,
        id AS sail
    FROM loads.sails
    JOIN indexed_positions
        ON loads.sails.position_id = indexed_positions.position

    UNION ALL

    SELECT
        id AS position,
        NULL::TEXT AS sail
    FROM loads.sail_positions
),
combinations AS (
    SELECT
        indexed_positions.position_index,
        ARRAY[options.sail]::TEXT[] AS sail_set
    FROM indexed_positions
    JOIN options
        ON options.position = indexed_positions.position
    WHERE indexed_positions.position_index = 1

    UNION ALL

    SELECT
        next_positions.position_index,
        combinations.sail_set || options.sail
    FROM combinations
    JOIN indexed_positions AS next_positions
        ON next_positions.position_index = combinations.position_index + 1
    JOIN options
        ON options.position = next_positions.position
),
complete_combinations AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY sail_set) - 1 id,
        sail_set
    FROM combinations
    WHERE position_index = (SELECT MAX(position_index) FROM indexed_positions)
),
flat_sail_sets AS (
    SELECT
        complete_combinations.id,
        indexed_positions.position,
        complete_combinations.sail_set[indexed_positions.position_index] AS sail
    FROM complete_combinations
    CROSS JOIN indexed_positions
)
INSERT INTO loads.sail_sets (sail_set_id, position_id, sail_id)
SELECT
    id,
    position,
    sail
FROM flat_sail_sets
ORDER BY id, position;

-- Define AWA ranges
INSERT INTO loads.awa_ranges (id, awa_range) VALUES
    ('upwind', '[0,60)'),
    ('reaching', '[60,120)'),
    ('downwind', '[120,180)');

-- Define AWS ranges
INSERT INTO loads.aws_ranges (aws_range) VALUES
    ('[0,10)'),
    ('[10,15)'),
    ('[15,20)'),
    ('[20,25)'),
    ('[25,30)'),
    ('[30,40)'),
    ('[40,)');

