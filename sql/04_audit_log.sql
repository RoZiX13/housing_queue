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