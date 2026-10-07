-- =====================================================================
-- NIVELSABER - Objetivos del estudiante
--
-- Tabla donde cada estudiante guarda sus propias metas (tipo + meta).
-- El avance NO se guarda: se calcula en cada petición con los datos
-- reales de la cuenta (prácticas, preguntas respondidas, áreas y
-- precisión), así un objetivo nuevo nunca muestra progreso inventado.
--
-- Tipos admitidos (vea TIPOS_OBJETIVO en backend/app.py):
--   preguntas -> respuestas dadas por el usuario
--   practicas -> prácticas terminadas
--   areas     -> áreas distintas practicadas
--   precision -> porcentaje global de aciertos
--
-- Ejecutar (es seguro varias veces, usa IF NOT EXISTS):
--   /opt/lampp/bin/mysql --default-character-set=utf8mb4 -u root nivelesaber < backend/objetivos.sql
-- =====================================================================

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS objetivos (
    id_objetivo INT NOT NULL AUTO_INCREMENT,
    id_usuario   INT NOT NULL,
    tipo         VARCHAR(20) NOT NULL,
    meta         INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_objetivo),
    KEY id_usuario (id_usuario),
    CONSTRAINT fk_objetivos_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Comprobación
DESCRIBE objetivos;
