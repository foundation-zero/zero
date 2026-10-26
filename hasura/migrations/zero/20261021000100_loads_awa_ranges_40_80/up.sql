-- Ordered so the ranges never overlap, which the EXCLUDE constraint checks per row.
UPDATE loads.awa_ranges SET awa_range = '[0,40)' WHERE id = 'upwind';
UPDATE loads.awa_ranges SET awa_range = '[40,80)' WHERE id = 'reaching';
UPDATE loads.awa_ranges SET awa_range = '[80,180)' WHERE id = 'downwind';
