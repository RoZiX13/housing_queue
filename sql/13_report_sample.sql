-- Пример выборки из отчёта с сортировкой:
SELECT *
 FROM v_queue_report
 ORDER BY
     organization = 'ИТОГО по всем предприятиям',
     organization,
     reason = 'ИТОГО по всем основаниям',
     reason;