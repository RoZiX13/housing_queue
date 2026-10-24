SELECT grantee, privilege_type
FROM information_schema.table_privileges
WHERE table_name = 'housing_queue';