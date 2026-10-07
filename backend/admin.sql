-- =====================================================================
-- NIVELSABER - Panel de administración
--
-- Qué hace:
--   1. Agrega la columna 'rol' a la tabla usuarios
--      ('estudiante' por defecto; los registros nuevos salen así).
--   2. Convierte en administrador la cuenta cuyo correo se indica
--      abajo (por defecto estudiante@gmail.com / feYalegria).
--
-- Es seguro ejecutarlo varias veces (no duplica nada).
--
-- Ejecutar:
--   /opt/lampp/bin/mysql --default-character-set=utf8mb4 -u root nivelesaber < backend/admin.sql
--
-- Para hacer admin otra cuenta:
--   UPDATE usuarios SET rol = 'admin' WHERE correo = 'su-correo@aqui.com';
-- =====================================================================

SET NAMES utf8mb4;

-- 1. Columna rol (IF NOT EXISTS lo soporta MariaDB 10.4)
ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS rol VARCHAR(20) NOT NULL DEFAULT 'estudiante' AFTER correo;

-- 2. El administrador. Cambia el correo si quieres otra cuenta.
UPDATE usuarios SET rol = 'admin' WHERE correo = 'estudiante@gmail.com';

-- 3. Comprobación
SELECT id_usuario, nombre, correo, rol FROM usuarios;
