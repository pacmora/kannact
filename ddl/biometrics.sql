-- Table: kannact.biometrics

DROP TABLE IF EXISTS kannact.biometrics;

CREATE TABLE IF NOT EXISTS kannact.biometrics
(
    patient_id bigint NOT NULL,
    biometrics_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1),
    test_date date,
    glucose smallint,
    systolic smallint,
    diastolic smallint,
    weight integer,
    CONSTRAINT biometric_id PRIMARY KEY (biometrics_id),
    CONSTRAINT patient_id FOREIGN KEY (patient_id)
        REFERENCES kannact.patients (patient_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS kannact.biometrics
    OWNER to postgres;
-- Index: biometrics_pagination_index

DROP INDEX IF EXISTS kannact.biometrics_pagination_index;

CREATE INDEX IF NOT EXISTS biometrics_pagination_index
    ON kannact.biometrics USING btree
    (biometrics_id DESC NULLS LAST, test_date DESC NULLS LAST)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;
