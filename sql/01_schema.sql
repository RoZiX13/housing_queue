-- ============================================================
-- Справочник областей
-- ============================================================
CREATE TABLE regions (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE
);

COMMENT ON TABLE regions IS 'Области';
COMMENT ON COLUMN regions.id IS 'Код области';
COMMENT ON COLUMN regions.name IS 'Наименование области';

-- ============================================================
-- Справочник городов
-- ============================================================
CREATE TABLE cities (
    id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name      varchar(100) NOT NULL,
    region_id integer NOT NULL REFERENCES regions(id) ON DELETE RESTRICT,
    CONSTRAINT cities_region_name_uniq UNIQUE (region_id, name)
);

COMMENT ON TABLE cities IS 'Города';
COMMENT ON COLUMN cities.id IS 'Код города';
COMMENT ON COLUMN cities.name IS 'Наименование города';
COMMENT ON COLUMN cities.region_id IS 'Код области';

-- ============================================================
-- Справочник организаций
-- ============================================================
CREATE TABLE organizations (
    id      integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name    varchar(200) NOT NULL,
    city_id integer NOT NULL REFERENCES cities(id) ON DELETE RESTRICT,
    CONSTRAINT organizations_city_name_uniq UNIQUE (city_id, name)
);

COMMENT ON TABLE organizations IS 'Организации';
COMMENT ON COLUMN organizations.id IS 'Код организации';
COMMENT ON COLUMN organizations.name IS 'Наименование организации';
COMMENT ON COLUMN organizations.city_id IS 'Код города';

-- ============================================================
-- Справочник оснований включения в очередь
-- ============================================================
CREATE TABLE inclusion_reasons (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name varchar(200) NOT NULL UNIQUE
);

COMMENT ON TABLE inclusion_reasons IS 'Основания включения в очередь';
COMMENT ON COLUMN inclusion_reasons.id IS 'Код основания';
COMMENT ON COLUMN inclusion_reasons.name IS 'Наименование основания';

-- ============================================================
-- Очередники
-- ============================================================
CREATE TABLE housing_queue (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    last_name       varchar(100) NOT NULL,
    queue_number    integer NOT NULL UNIQUE,
    order_number    varchar(50),
    organization_id integer NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    reason_id       integer NOT NULL REFERENCES inclusion_reasons(id) ON DELETE RESTRICT,
    inclusion_date  date NOT NULL,
    passport_data   text NOT NULL,
    family_members  integer NOT NULL CHECK (family_members >= 1),
    address         text NOT NULL
);

COMMENT ON TABLE housing_queue IS 'Очередники на получение жилья';
COMMENT ON COLUMN housing_queue.id IS 'Идентификатор записи';
COMMENT ON COLUMN housing_queue.last_name IS 'Фамилия';
COMMENT ON COLUMN housing_queue.queue_number IS 'Номер очереди';
COMMENT ON COLUMN housing_queue.order_number IS 'Номер приказа';
COMMENT ON COLUMN housing_queue.organization_id IS 'Код организации';
COMMENT ON COLUMN housing_queue.reason_id IS 'Код основания включения в очередь';
COMMENT ON COLUMN housing_queue.inclusion_date IS 'Дата включения в очередь';
COMMENT ON COLUMN housing_queue.passport_data IS 'Паспортные данные';
COMMENT ON COLUMN housing_queue.family_members IS 'Число членов семьи';
COMMENT ON COLUMN housing_queue.address IS 'Адрес';

-- Индексы для отчётов и поиска
CREATE INDEX idx_housing_queue_organization ON housing_queue(organization_id);
CREATE INDEX idx_housing_queue_reason       ON housing_queue(reason_id);
CREATE INDEX idx_housing_queue_date         ON housing_queue(inclusion_date);
CREATE INDEX idx_housing_queue_last_name    ON housing_queue(last_name);

-- ============================================================
-- Представление для отчёта:
-- по предприятиям и основаниям включения в очередь
-- с итогами по предприятиям, основаниям и общим итогом
-- ============================================================
CREATE VIEW v_queue_report AS
SELECT
    CASE
        WHEN GROUPING(o.name) = 1 THEN 'ИТОГО по всем предприятиям'
        ELSE o.name
    END AS organization,
    CASE
        WHEN GROUPING(r.name) = 1 THEN 'ИТОГО по всем основаниям'
        ELSE r.name
    END AS reason,
    COUNT(*) AS queue_count
FROM housing_queue q
JOIN organizations o      ON o.id = q.organization_id
JOIN inclusion_reasons r  ON r.id = q.reason_id
GROUP BY GROUPING SETS (
    (o.name, r.name),  -- детализация: предприятие + основание
    (o.name),          -- итог по предприятию
    (r.name),          -- итог по основанию
    ()                 -- общий итог
);

COMMENT ON VIEW v_queue_report IS
'Отчёт по предприятиям и основаниям включения в очередь с итогами';

-- Пример выборки из отчёта с сортировкой:
-- SELECT *
-- FROM v_queue_report
-- ORDER BY
--     organization = 'ИТОГО по всем предприятиям',
--     organization,
--     reason = 'ИТОГО по всем основаниям',
--     reason;