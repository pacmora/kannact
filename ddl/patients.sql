-- Table: kannact.patients

DROP TABLE IF EXISTS kannact.patients;

CREATE TABLE IF NOT EXISTS kannact.patients
(
    patient_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    name text COLLATE pg_catalog."default",
    date_of_birth date,
    gender text COLLATE pg_catalog."default",
    sex text COLLATE pg_catalog."default",
    address text COLLATE pg_catalog."default",
    email text COLLATE pg_catalog."default",
    phone text COLLATE pg_catalog."default",
    CONSTRAINT patients_pkey PRIMARY KEY (patient_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS kannact.patients
    OWNER to postgres;
-- Index: patient_email_index

DROP INDEX IF EXISTS kannact.patient_email_index;

CREATE INDEX IF NOT EXISTS patient_email_index
    ON kannact.patients USING hash
    (email COLLATE pg_catalog."C.utf8" text_pattern_ops)
    TABLESPACE pg_default;
-- Index: patients_patient_id_index

DROP INDEX IF EXISTS kannact.patients_patient_id_index;

CREATE INDEX IF NOT EXISTS patients_patient_id_index
    ON kannact.patients USING btree
    (patient_id ASC NULLS LAST)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;