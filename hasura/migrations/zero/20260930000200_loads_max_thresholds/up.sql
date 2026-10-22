-- Thresholds per variable, used wherever a reference value leaves a threshold empty.
CREATE TABLE loads.max_thresholds (
    variable_id TEXT PRIMARY KEY,
    alarm_low NUMERIC,
    warning_low NUMERIC,
    warning_high NUMERIC,
    alarm_high NUMERIC,
    CHECK (
        (alarm_low IS NULL OR warning_low IS NULL OR alarm_low <= warning_low) AND
        (alarm_low IS NULL OR warning_high IS NULL OR alarm_low <= warning_high) AND
        (alarm_low IS NULL OR alarm_high IS NULL OR alarm_low <= alarm_high) AND
        (warning_low IS NULL OR warning_high IS NULL OR warning_low <= warning_high) AND
        (warning_low IS NULL OR alarm_high IS NULL OR warning_low <= alarm_high) AND
        (warning_high IS NULL OR alarm_high IS NULL OR warning_high <= alarm_high)
    )
);
