ALTER TABLE loads.thresholds RENAME CONSTRAINT thresholds_check TO max_thresholds_check;
ALTER TABLE loads.thresholds RENAME CONSTRAINT thresholds_pkey TO max_thresholds_pkey;
ALTER TABLE loads.thresholds RENAME TO max_thresholds;
