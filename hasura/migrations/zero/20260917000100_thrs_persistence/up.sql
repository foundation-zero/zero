CREATE TABLE IF NOT EXISTS thrs.module_persistence (
    module_name VARCHAR NOT NULL,
    parameters JSONB,
    manual_control_values JSONB,
    automation_mode VARCHAR NOT NULL DEFAULT 'manual',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (module_name)
);

CREATE INDEX IF NOT EXISTS idx_module_persistence_updated_at
    ON thrs.module_persistence (updated_at DESC);
