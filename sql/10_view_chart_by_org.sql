CREATE VIEW v_chart_queue_by_org AS
SELECT
    o.name AS organization,
    COUNT(*) AS total_queue
FROM housing_queue q
JOIN organizations o ON o.id = q.organization_id
GROUP BY o.name
ORDER BY total_queue DESC;