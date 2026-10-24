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