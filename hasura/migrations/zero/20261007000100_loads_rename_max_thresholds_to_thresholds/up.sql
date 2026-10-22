ALTER TABLE loads.max_thresholds RENAME TO thresholds;
ALTER TABLE loads.thresholds RENAME CONSTRAINT max_thresholds_pkey TO thresholds_pkey;
ALTER TABLE loads.thresholds RENAME CONSTRAINT max_thresholds_check TO thresholds_check;
