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