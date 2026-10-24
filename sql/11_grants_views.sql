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