-- =====================================================================
-- NIVELSABER - Semilla de la base de datos
--
-- Contenido:
--   1. Migración de esquema: utf8mb4 + respuestas_usuario.id_resultado
--   2. 5 áreas
--   3. 1 usuario de prueba (estudiante@gmail.com / feYalegria)
--   4. 25 preguntas (5 por área) y 100 opciones (A-D)
--
-- Ejecutar:
--   /opt/lampp/bin/mysql --default-character-set=utf8mb4 -u root nivelesaber < backend/semillas.sql
--
-- IMPORTANTE: borra todas las preguntas (y en cascada las opciones y las
-- respuestas que las referencian). Los resultados se conservan porque el
-- id de las áreas no cambia.
-- =====================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- 1. Migración de esquema (idempotente)
-- ---------------------------------------------------------------------

ALTER TABLE areas
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE preguntas
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE opciones
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE usuarios
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE respuestas_usuario
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE resultados
    CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- Columna id_resultado (IF NOT EXISTS lo soporta MariaDB 10.4)
ALTER TABLE respuestas_usuario
    ADD COLUMN IF NOT EXISTS id_resultado INT NULL AFTER id_opcion;

-- Llave foránea solo si todavía no existe. Se usa PREPARE porque
-- ALTER TABLE ... ADD CONSTRAINT no admite IF NOT EXISTS.
SET @existe_fk = (
    SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME   = 'respuestas_usuario'
      AND COLUMN_NAME  = 'id_resultado'
      AND REFERENCED_TABLE_NAME = 'resultados'
);

SET @sql = IF(@existe_fk = 0,
    'ALTER TABLE respuestas_usuario ADD CONSTRAINT fk_ru_resultado FOREIGN KEY (id_resultado) REFERENCES resultados (id_resultado) ON DELETE CASCADE ON UPDATE CASCADE',
    'DO 0');

PREPARE sentencia FROM @sql;
EXECUTE sentencia;
DEALLOCATE PREPARE sentencia;

-- ---------------------------------------------------------------------
-- 2. Áreas
-- ---------------------------------------------------------------------

INSERT INTO areas (nombre_area) VALUES
    ('Lectura Crítica'),
    ('Matemáticas'),
    ('Ciencias Naturales'),
    ('Sociales y Ciudadanas'),
    ('Inglés')
ON DUPLICATE KEY UPDATE nombre_area = VALUES(nombre_area);

SET @a_lectura   = (SELECT id_area FROM areas WHERE nombre_area = 'Lectura Crítica');
SET @a_mate      = (SELECT id_area FROM areas WHERE nombre_area = 'Matemáticas');
SET @a_naturales = (SELECT id_area FROM areas WHERE nombre_area = 'Ciencias Naturales');
SET @a_sociales  = (SELECT id_area FROM areas WHERE nombre_area = 'Sociales y Ciudadanas');
SET @a_ingles    = (SELECT id_area FROM areas WHERE nombre_area = 'Inglés');

-- ---------------------------------------------------------------------
-- 3. Usuario de prueba
--     contraseña: feYalegria
--     hash: werkzeug generate_password_hash(method="pbkdf2:sha256")
-- ---------------------------------------------------------------------

INSERT INTO usuarios (nombre, apellido, correo, contrasena) VALUES
    ('Estudiante', 'Demo', 'estudiante@gmail.com',
     'pbkdf2:sha256:1000000$BIcb01iMVGBVFC7f$a2629401d64b1d90d9e4ef7cf23dadf6bd7aa219858ede36cada37028f6bcd01')
ON DUPLICATE KEY UPDATE
    nombre     = VALUES(nombre),
    apellido   = VALUES(apellido),
    contrasena = VALUES(contrasena);

-- ---------------------------------------------------------------------
-- 4. Preguntas y opciones
-- ---------------------------------------------------------------------

DELETE FROM preguntas;

-- ----- Lectura Crítica ------------------------------------------------

INSERT INTO preguntas (id_area, numero_pregunta, modulo, tema, enunciado, retroalimentacion) VALUES
(@a_lectura, 1, 'Comprensión lectora', 'Inferencia',
 'Lee el siguiente fragmento: "El cielo estaba oscuro y los pájaros volaban en círculos. Pronto, las primeras gotas empezaron a caer." ¿Qué se infiere del texto?',
 'El cielo oscuro y las "primeras gotas" son indicios directos y explícitos de que está comenzando a llover.'),
(@a_lectura, 2, 'Comprensión lectora', 'Idea central',
 'Lee: "Aunque llegamos tarde al concierto, pudimos disfrutar la última canción." ¿Cuál es la idea central del fragmento?',
 'El texto tiene dos partes: el inconveniente (llegar tarde) y el beneficio (disfrutar). Se expresa una concesión, así que la idea central es que, aunque tarde, aún se aprovechó la oportunidad.'),
(@a_lectura, 3, 'Argumentación', 'Hecho y opinión',
 '¿Cuál de las siguientes oraciones es una OPINIÓN?',
 'Una opinión expresa un juicio personal que puede coincidir o no con otras personas. Los demás enunciados son hechos verificables con evidencia.'),
(@a_lectura, 4, 'Comprensión lectora', 'Conectores',
 '"No estudió para el examen; ______, obtuvo una nota baja." ¿Qué conector completa mejor la oración?',
 'La segunda parte es la consecuencia de la primera, así que se necesita un conector consecutivo: "por lo tanto". "Sin embargo" introduce una contraposición, no una consecuencia.'),
(@a_lectura, 5, 'Argumentación', 'Tesis y argumentos',
 'En el texto "Debemos reducir el uso de plásticos porque tardan siglos en degradarse y contaminan los océanos", ¿cuál es el argumento?',
 'La tesis es "debemos reducir el uso de plásticos" y la razón que la sustenta es el dato sobre el tiempo de degradación y la contaminación. El argumento es siempre la razón, no la conclusión.');

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Que está amaneciendo.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'B', 'Que va a llover.', 1 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'C', 'Que es invierno.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'D', 'Que hay un eclipse.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 1;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'El concierto fue un fracaso.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'B', 'Aunque tarde, aún se aprovechó la oportunidad.', 1 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'C', 'Siempre es mejor llegar temprano.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'D', 'Las canciones duraban poco.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 2;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'El río Bogotá nace en el páramo de Guachené.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'B', 'Leer todos los días mejora la comprensión.', 1 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'C', 'Colombia tiene 32 departamentos.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'D', 'El agua hierve a 100 °C.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 3;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'sin embargo', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'B', 'por lo tanto', 1 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'C', 'además', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'D', 'por ejemplo', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 4;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Que los plásticos son útiles.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'B', 'Que tardan siglos en degradarse y contaminan los océanos.', 1 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'C', 'Que debemos reducirlos.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'D', 'Que los océanos están secos.', 0 FROM preguntas WHERE id_area = @a_lectura AND numero_pregunta = 5;

-- ----- Matemáticas ----------------------------------------------------

INSERT INTO preguntas (id_area, numero_pregunta, modulo, tema, enunciado, retroalimentacion) VALUES
(@a_mate, 1, 'Razonamiento', 'Velocidad, tiempo y distancia',
 'Si un vehículo va a 60 km/h, ¿cuánta distancia recorre en 2.5 horas?',
 'Para hallar la distancia multiplicas Velocidad × Tiempo (60 × 2.5) = 150 km.'),
(@a_mate, 2, 'Aritmética', 'Porcentajes',
 'En una tienda, una mochila cuesta $80.000 y tiene un descuento del 25%. ¿Cuál es el precio final?',
 'El 25% de 80.000 es 20.000. El precio final es 80.000 − 20.000 = 60.000.'),
(@a_mate, 3, 'Álgebra', 'Ecuaciones lineales',
 'Si 3x + 5 = 20, ¿cuánto vale x?',
 'Pasa el 5 restando: 3x = 20 − 5 = 15. Luego divide entre 3: x = 15 ÷ 3 = 5.'),
(@a_mate, 4, 'Geometría', 'Ángulos',
 'Dos ángulos son complementarios y uno mide 35°. ¿Cuánto mide el otro?',
 'Los ángulos complementarios suman 90°: 90 − 35 = 55°. Si sumaran 180° serían suplementarios.'),
(@a_mate, 5, 'Probabilidad y estadística', 'Mediana',
 '¿Cuál es la mediana del conjunto 4, 7, 9, 2, 6?',
 'Primero se ordena: 2, 4, 6, 7, 9. La mediana es el valor central de la lista ordenada, es decir el tercero: 6.');

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', '120 km', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'B', '150 km', 1 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'C', '180 km', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'D', '200 km', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 1;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', '$20.000', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'B', '$60.000', 1 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'C', '$75.000', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'D', '$65.000', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 2;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', '3', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'B', '4', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'C', '5', 1 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'D', '6', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 3;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', '35°', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'B', '55°', 1 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'C', '145°', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'D', '180°', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 4;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', '4', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'B', '6', 1 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'C', '7', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'D', '9', 0 FROM preguntas WHERE id_area = @a_mate AND numero_pregunta = 5;

-- ----- Ciencias Naturales --------------------------------------------

INSERT INTO preguntas (id_area, numero_pregunta, modulo, tema, enunciado, retroalimentacion) VALUES
(@a_naturales, 1, 'Biología', 'Célula y energía',
 '¿Qué organelo celular es el principal responsable de producir energía a través de la respiración celular?',
 'Las mitocondrias son conocidas como las "centrales de energía" de la célula, ya que generan la mayor parte del ATP.'),
(@a_naturales, 2, 'Química', 'Estados de la materia',
 '¿Qué cambio de estado ocurre cuando el agua pasa de líquido a vapor?',
 'Evaporación es el paso de líquido a gas. Fusión es de sólido a líquido, condensación de gas a líquido y sublimación de sólido a gas.'),
(@a_naturales, 3, 'Biología', 'Fotosíntesis',
 '¿Qué gas liberan las plantas durante la fotosíntesis?',
 'En la fotosíntesis las plantas absorben dióxido de carbono y liberan oxígeno como producto final.'),
(@a_naturales, 4, 'Biología', 'Sistema circulatorio',
 '¿Cuál es la función principal de los glóbulos rojos?',
 'La hemoglobina de los glóbulos rojos se une al oxígeno y lo transporta desde los pulmones hasta todos los órganos. Combatir infecciones es tarea de los glóbulos blancos.'),
(@a_naturales, 5, 'Química', 'Tabla periódica',
 '¿Qué elemento tiene el símbolo "Fe"?',
 'Fe proviene del latín "ferrum" y corresponde al hierro, de número atómico 26. F es flúor y P es fósforo.');

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Núcleo', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'B', 'Mitocondria', 1 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'C', 'Ribosoma', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'D', 'Cloroplasto', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 1;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Fusión', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'B', 'Condensación', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'C', 'Evaporación', 1 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'D', 'Sublimación', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 2;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Dióxido de carbono', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'B', 'Nitrógeno', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'C', 'Oxígeno', 1 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'D', 'Metano', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 3;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Coagular la sangre', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'B', 'Transportar oxígeno', 1 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'C', 'Combatir infecciones', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'D', 'Producir hormonas', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 4;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Flúor', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'B', 'Fermio', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'C', 'Hierro', 1 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'D', 'Fósforo', 0 FROM preguntas WHERE id_area = @a_naturales AND numero_pregunta = 5;

-- ----- Sociales y Ciudadanas ------------------------------------------

INSERT INTO preguntas (id_area, numero_pregunta, modulo, tema, enunciado, retroalimentacion) VALUES
(@a_sociales, 1, 'Geografía', 'División político-territorial',
 '¿Cuál es la capital del departamento del Cauca?',
 'Popayán es la capital del Cauca y una de las ciudades más antiguas de Colombia.'),
(@a_sociales, 2, 'Estado colombiano', 'Constitución',
 '¿En qué año se promulgó la Constitución Política de Colombia vigente?',
 'La Constitución de 1991 reemplazó la de 1886 y entró en vigencia el 5 de julio de 1991.'),
(@a_sociales, 3, 'Geografía', 'División político-territorial',
 '¿Cuántos departamentos tiene Colombia?',
 'Colombia está dividida en 32 departamentos. A ellos se suma el Distrito Capital de Bogotá.'),
(@a_sociales, 4, 'Democracia', 'Soberanía',
 'En una democracia, ¿quién ostenta la soberanía?',
 'El artículo 3 de la Constitución establece que la soberanía reside exclusivamente en el pueblo, el cual la ejerce a través de sus representantes.'),
(@a_sociales, 5, 'Estado colombiano', 'Organización del Estado',
 '¿Cuál es la función principal del Congreso de la República?',
 'El Congreso se compone de la Cámara de Representantes y el Senado, y su función es expedir las leyes. Administrar justicia corresponde al poder judicial.');

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Popayán', 1 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'B', 'Neiva', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'C', 'Florencia', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'D', 'Ibagué', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 1;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', '1886', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'B', '1936', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'C', '1991', 1 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'D', '2011', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 2;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', '12', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'B', '22', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'C', '32', 1 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'D', '40', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 3;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'El presidente', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'B', 'El poder judicial', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'C', 'El pueblo', 1 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'D', 'Las fuerzas militares', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 4;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Administrar la justicia', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'B', 'Expedir leyes', 1 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'C', 'Comandar el ejército', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'D', 'Administrar los impuestos', 0 FROM preguntas WHERE id_area = @a_sociales AND numero_pregunta = 5;

-- ----- Inglés ----------------------------------------------------------

INSERT INTO preguntas (id_area, numero_pregunta, modulo, tema, enunciado, retroalimentacion) VALUES
(@a_ingles, 1, 'Reading', 'Notices',
 'Where can you see this notice? "PLEASE DO NOT FEED THE ANIMALS"',
 'The notice says "please do not feed the animals", which is a common rule in a zoo.'),
(@a_ingles, 2, 'Grammar', 'Present simple',
 'Choose the correct sentence.',
 'In the present simple, third person singular subjects (she / he / it) take the verb with -s or -es: "She goes to school every day."'),
(@a_ingles, 3, 'Vocabulary', 'Antonyms',
 'What is the opposite of "expensive"?',
 'Expensive means costing a lot of money. Its opposite is cheap. Loud, heavy and fast describe other qualities.'),
(@a_ingles, 4, 'Grammar', 'Prepositions of time',
 'The meeting is ___ Monday ___ 9 a.m.',
 'We use "on" with days (on Monday) and "at" with clock times (at 9 a.m.). "In" is used with months and years.'),
(@a_ingles, 5, 'Reading', 'Comprehension',
 '"The library closes at 6 p.m. Please return your books before that time." Where would you see this notice?',
 'The notice mentions the library and returning books, so it is clearly posted in a library.');

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'In a hospital', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'B', 'In a train station', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'C', 'In a zoo', 1 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 1
UNION ALL SELECT id_pregunta, 'D', 'In a school', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 1;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'She go to school every day.', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'B', 'She goes to school every day.', 1 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'C', 'She going to school every day.', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 2
UNION ALL SELECT id_pregunta, 'D', 'She is go to school every day.', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 2;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'Cheap', 1 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'B', 'Loud', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'C', 'Heavy', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 3
UNION ALL SELECT id_pregunta, 'D', 'Fast', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 3;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'in / at', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'B', 'on / at', 1 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'C', 'at / on', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 4
UNION ALL SELECT id_pregunta, 'D', 'on / in', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 4;

INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
SELECT id_pregunta, 'A', 'In a restaurant', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'B', 'In a library', 1 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'C', 'At a bus stop', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 5
UNION ALL SELECT id_pregunta, 'D', 'In a hospital', 0 FROM preguntas WHERE id_area = @a_ingles AND numero_pregunta = 5;

-- ---------------------------------------------------------------------
-- Resumen
-- ---------------------------------------------------------------------
SELECT a.nombre_area AS area,
       COUNT(DISTINCT p.id_pregunta) AS preguntas,
       COUNT(o.id_opcion)            AS opciones
FROM areas a
LEFT JOIN preguntas p ON p.id_area = a.id_area
LEFT JOIN opciones o ON o.id_pregunta = p.id_pregunta
GROUP BY a.id_area, a.nombre_area
ORDER BY a.id_area;
