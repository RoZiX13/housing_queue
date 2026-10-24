-- Администратор: все права на все таблицы и последовательности
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO housing_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO housing_admin;

-- Оператор: может читать и изменять данные в основной таблице и справочниках
GRANT SELECT, INSERT, UPDATE, DELETE ON housing_queue TO housing_operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON organizations TO housing_operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON inclusion_reasons TO housing_operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON cities TO housing_operator;
GRANT SELECT, INSERT, UPDATE, DELETE ON regions TO housing_operator;

-- Аналитик: может только читать данные (для отчетов)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO housing_analyst;