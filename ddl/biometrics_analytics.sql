- Table: kannact.biometrics_analytics

-- DROP TABLE IF EXISTS kannact.biometrics_analytics;

CREATE TABLE IF NOT EXISTS kannact.biometrics_analytics
(
    patient_id bigint NOT NULL,
    glucose_mean integer,
    glucose_min integer,
    glucose_max integer,
    systolic_mean integer,
    systolic_min integer,
    systolic_max integer,
    diastolic_mean integer,
    diastolic_min integer,
    diastolic_max integer,
    weight_mean integer,
    weight_min integer,
    weight_max integer,
    CONSTRAINT biometrics_analytics_pkey PRIMARY KEY (patient_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS kannact.biometrics_analytics
    OWNER to postgres;
-- Index: biometrics_analytics_patient_id_index

DROP INDEX IF EXISTS kannact.biometrics_analytics_patient_id_index;

CREATE INDEX IF NOT EXISTS biometrics_analytics_patient_id_index
    ON kannact.biometrics_analytics USING btree
    (patient_id ASC NULLS LAST)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;