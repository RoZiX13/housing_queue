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