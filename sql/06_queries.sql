-- Пример выборки из отчёта с сортировкой:
SELECT *
 FROM v_queue_report
 ORDER BY
     organization = 'ИТОГО по всем предприятиям',
     organization,
     reason = 'ИТОГО по всем основаниям',
     reason;

-- Проверка прав на таблицу housing_queue
SELECT grantee, privilege_type
FROM information_schema.table_privileges
WHERE table_name = 'housing_queue';
