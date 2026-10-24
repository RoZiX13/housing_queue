-- Пользователь с полными правами (администратор БД)
CREATE ROLE housing_admin WITH LOGIN PASSWORD 'StrongAdminPass123';

-- Пользователь для ввода данных (оператор)
CREATE ROLE housing_operator WITH LOGIN PASSWORD 'OperatorPass456';

-- Пользователь для просмотра отчетов (аналитик)
CREATE ROLE housing_analyst WITH LOGIN PASSWORD 'AnalystPass789';