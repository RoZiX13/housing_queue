CREATE TABLE audit_log (
    audit_id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name   text        NOT NULL,
    operation    text        NOT NULL, -- INSERT, UPDATE, DELETE
    record_id    bigint,               -- ID измененной записи
    old_data     jsonb,                -- Данные ДО изменения
    new_data     jsonb,                -- Данные ПОСЛЕ изменения
    changed_by   text        NOT NULL DEFAULT session_user,
    changed_at   timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE audit_log IS 'Журнал аудита всех изменений в таблицах';

CREATE OR REPLACE FUNCTION log_audit_changes()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, record_id, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.id, to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.id, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_data)
        VALUES (TG_TABLE_NAME, TG_OP, OLD.id, to_jsonb(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_housing_queue_audit
AFTER INSERT OR UPDATE OR DELETE ON housing_queue
FOR EACH ROW EXECUTE FUNCTION log_audit_changes();
