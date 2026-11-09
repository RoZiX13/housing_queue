CREATE VIEW v_housing_queue_full AS
SELECT
    q.queue_number,
    q.last_name,
    q.order_number,
    o.name AS organization_name,
    r.name AS reason_name,
    c.name AS city_name,
    reg.name AS region_name,
    q.inclusion_date,
    q.family_members,
    q.address
FROM housing_queue q
JOIN organizations o      ON o.id = q.organization_id
JOIN cities c             ON c.id = o.city_id
JOIN regions reg          ON reg.id = c.region_id
JOIN inclusion_reasons r  ON r.id = q.reason_id;

CREATE VIEW v_cross_org_reason AS
SELECT
    o.name AS organization,
    COUNT(*) FILTER (WHERE r.name = 'Малоимущая семья')      AS "Малоимущие",
    COUNT(*) FILTER (WHERE r.name = 'Ветхое жильё')           AS "Ветхое жильё",
    COUNT(*) FILTER (WHERE r.name = 'Многодетная семья')     AS "Многодетные",
    COUNT(*) FILTER (WHERE r.name = 'Молодая семья')         AS "Молодые",
    COUNT(*) FILTER (WHERE r.name = 'Инвалид / заболевание') AS "Инвалиды",
    COUNT(*) FILTER (WHERE r.name = 'Работник бюджетной сферы') AS "Бюджетники"
FROM housing_queue q
JOIN organizations o     ON o.id = q.organization_id
JOIN inclusion_reasons r ON r.id = q.reason_id
GROUP BY o.name;

CREATE VIEW v_queue_totals AS
SELECT
    COALESCE(o.name, 'ИТОГО по всем организациям') AS organization,
    COALESCE(r.name, 'ИТОГО по всем основаниям')   AS reason,
    COUNT(*) AS queue_count
FROM housing_queue q
JOIN organizations o     ON o.id = q.organization_id
JOIN inclusion_reasons r ON r.id = q.reason_id
GROUP BY GROUPING SETS (
    (o.name, r.name),  -- Детализация
    (o.name),          -- Итог по организации
    (r.name),          -- Итог по основанию
    ()                 -- Общий итог
);

CREATE VIEW v_chart_queue_by_org AS
SELECT
    o.name AS organization,
    COUNT(*) AS total_queue
FROM housing_queue q
JOIN organizations o ON o.id = q.organization_id
GROUP BY o.name
ORDER BY total_queue DESC;

-- 1. Разрешаем роли использовать схему public (если ещё нет)
GRANT USAGE ON SCHEMA public TO housing_admin;

-- 2. Выдаём право SELECT на все существующие представления
GRANT SELECT ON 
    v_housing_queue_full,
    v_cross_org_reason,
    v_queue_totals,
    v_chart_queue_by_org
TO housing_admin;

-- 3. (Опционально) Выдаём права на будущие представления,
--    которые вы можете создать позже
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO housing_admin;
