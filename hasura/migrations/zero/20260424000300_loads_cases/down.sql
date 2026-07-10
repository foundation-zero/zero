TRUNCATE TABLE
  loads.reference_values,
  loads.load_cases,
  loads.aws_ranges,
  loads.awa_ranges,
  loads.sail_sets,
  loads.sails,
  loads.sail_positions
RESTART IDENTITY CASCADE;
