"""Carga 25 talleres originales (10 preguntas por taller) sin borrar datos."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

TALLERES = {
    "Lectura Crítica": [
        ("Taller 1 - Inferencias", [
            ("El bus llegó empapado y varias personas cerraban sus paraguas. ¿Qué se infiere?", "Acaba de llover."),
            ("Lucía miró el reloj, guardó los libros y corrió hacia la puerta. ¿Qué probablemente hará?", "Saldrá con prisa."),
            ("El restaurante estaba lleno y varias personas esperaban afuera. ¿Qué se puede deducir?", "Había más clientes que mesas disponibles."),
            ("Al abrir la ventana, Mateo vio ramas moviéndose con fuerza. ¿Qué condición se infiere?", "Hay viento fuerte."),
            ("El suelo del parque tenía charcos y las nubes empezaban a despejarse. ¿Qué ocurrió antes?", "Llovió recientemente."),
            ("Elena llevó una linterna y una chaqueta al sótano sin ventanas. ¿Por qué probablemente?", "El lugar puede estar oscuro y frío."),
            ("La tienda bajó las luces y el encargado cerró la caja. ¿Qué probablemente ocurrirá?", "La tienda cerrará pronto."),
            ("El perro olfateó la puerta y movió la cola al oír unas llaves. ¿Qué espera?", "Que alguien llegue a casa."),
            ("El camino estaba cubierto de hojas amarillas y naranjas. ¿En qué estación podría estar?", "En otoño."),
            ("La profesora repartió hojas y pidió guardar los celulares. ¿Qué actividad parece comenzar?", "Una evaluación escrita."),
        ]),
        ("Taller 2 - Ideas y estructura", [
            ("Un párrafo explica que caminar diariamente mejora la salud y reduce el estrés. ¿Cuál es su idea central?", "Caminar con regularidad aporta beneficios para la salud."),
            ("Un texto presenta primero un problema de basura y luego varias soluciones. ¿Qué estructura usa?", "Problema y solución."),
            ("Una noticia responde qué ocurrió, dónde y cuándo. ¿Qué información organiza?", "Los datos principales de un hecho."),
            ("Un texto compara la educación presencial con la virtual. ¿Cuál es su propósito estructural?", "Mostrar semejanzas y diferencias."),
            ("Un párrafo enumera causas de la erosión y sus consecuencias. ¿Qué relación desarrolla?", "Causa y efecto."),
            ("La oración inicial anuncia que el agua es un recurso limitado y el resto aporta razones. ¿Qué función tiene?", "Presentar la idea principal."),
            ("Un texto empieza con una afirmación general y termina con ejemplos concretos. ¿Cómo organiza la información?", "De lo general a lo particular."),
            ("Una conclusión retoma la tesis y resume las razones expuestas. ¿Qué función cumple?", "Cerrar y sintetizar el argumento."),
            ("Un instructivo presenta materiales y luego pasos numerados. ¿Qué organización predomina?", "Secuencial."),
            ("Un artículo explica el significado de un término y ofrece ejemplos. ¿Qué organización predomina?", "Definición y ejemplificación."),
        ]),
        ("Taller 3 - Argumentos y postura", [
            ("“La biblioteca debe ampliar su horario porque muchos estudiantes trabajan de día”. ¿Cuál es la tesis?", "La biblioteca debe ampliar su horario."),
            ("En la misma afirmación, ¿qué razón apoya la tesis?", "Muchos estudiantes trabajan durante el día."),
            ("¿Cuál enunciado es una opinión y no un dato verificable?", "La lectura es la actividad más agradable."),
            ("Un autor cita un estudio con metodología y resultados. ¿Qué tipo de apoyo presenta?", "Evidencia basada en investigación."),
            ("¿Qué debe hacer un contraargumento sólido?", "Presentar una objeción relevante y responderla con razones."),
            ("“Todos lo hacen, así que debe ser correcto”. ¿Qué falla presenta este argumento?", "Confunde popularidad con validez."),
            ("¿Cuál es la conclusión de “Como el transporte reduce emisiones, conviene usarlo más”?", "Conviene usar más el transporte que reduce emisiones."),
            ("Una encuesta pequeña se usa para afirmar lo que piensa toda una ciudad. ¿Qué problema hay?", "La muestra puede no representar a toda la ciudad."),
            ("¿Qué diferencia un argumento de una afirmación aislada?", "El argumento ofrece razones o evidencias para sostenerla."),
            ("Un texto reconoce una limitación y luego defiende su propuesta con datos. ¿Qué muestra?", "Una postura razonada que considera objeciones."),
        ]),
        ("Taller 4 - Conectores y sentido", [
            ("“Estudió con anticipación; ___, resolvió el examen con confianza”. Completa la relación.", "por eso"),
            ("“El camino era largo; ___, continuaron caminando”. Completa la oposición.", "sin embargo"),
            ("“Llevó agua ___ una fruta para el recorrido”. Completa la adición.", "y"),
            ("“No asistió a clase ___ tenía una cita médica”. Completa la causa.", "ya que"),
            ("“Primero mezcla los ingredientes; ___, hornea la preparación”. Completa la secuencia.", "después"),
            ("“El informe presenta datos; ___, incluye testimonios”. Completa la adición.", "además"),
            ("“El equipo entrenó; ___, no logró clasificar”. Completa el contraste.", "aun así"),
            ("“El río creció ___ llovió durante varias horas”. Completa la causa.", "porque"),
            ("“La propuesta es económica; ___, puede aplicarse pronto”. Completa la consecuencia.", "por lo tanto"),
            ("“El texto es breve; ___, desarrolla varias ideas”. Completa la concesión.", "aunque"),
        ]),
        ("Taller 5 - Lectura crítica", [
            ("Una gráfica muestra ventas mensuales, pero no indica la unidad de medida. ¿Qué conviene verificar?", "Qué unidad representa cada valor."),
            ("Una noticia solo cita a la empresa involucrada en una controversia. ¿Qué falta?", "Incluir otras fuentes pertinentes."),
            ("Una fotografía acompaña un artículo sobre contaminación. ¿Qué no demuestra por sí sola?", "La causa exacta del problema."),
            ("Un anuncio afirma “el producto número uno” sin mostrar datos. ¿Qué debe preguntarse el lector?", "Qué evidencia respalda esa afirmación."),
            ("Dos columnas de una gráfica comienzan en escalas distintas. ¿Qué riesgo existe?", "Que la diferencia visual exagere la comparación."),
            ("Un informe fue publicado hace veinte años sobre tecnología actual. ¿Qué aspecto revisar?", "Si sus datos siguen vigentes."),
            ("Un texto presenta porcentajes, pero omite el número de personas encuestadas. ¿Qué dato falta?", "El tamaño de la muestra."),
            ("Una fuente explica quién financió el estudio. ¿Por qué importa?", "Permite valorar posibles intereses o sesgos."),
            ("Una publicación comparte una frase sin autor ni contexto. ¿Qué se debe hacer?", "Verificar el origen y el contexto antes de aceptarla."),
            ("Una tabla compara ciudades con poblaciones muy diferentes usando totales. ¿Qué comparación sería más justa?", "Usar tasas relativas o valores por habitante."),
        ]),
    ],
    "Matemáticas": [
        ("Taller 1 - Aritmética y porcentajes", [
            ("Un cuaderno cuesta $20.000 y tiene 15% de descuento. ¿Cuál es el precio final?", "$17.000."),
            ("¿Cuánto es el 30% de 250?", "75."),
            ("Una receta usa 3 tazas para 6 porciones. ¿Cuántas para 10 porciones?", "5 tazas."),
            ("Un precio sube de $40.000 a $50.000. ¿Cuál fue el aumento porcentual?", "25%."),
            ("¿Cuál fracción es equivalente a 3/4?", "6/8."),
            ("Un tanque contiene 2/5 de su capacidad de 100 litros. ¿Cuántos litros tiene?", "40 litros."),
            ("Si 8 lápices cuestan $12.000, ¿cuánto cuestan 5 al mismo precio unitario?", "$7.500."),
            ("¿Cuál es el resultado de 2,4 + 0,75?", "3,15."),
            ("Un artículo de $80.000 aumenta 10%. ¿Cuál es el nuevo precio?", "$88.000."),
            ("Se reparten 84 fichas por igual entre 7 equipos. ¿Cuántas recibe cada uno?", "12 fichas."),
        ]),
        ("Taller 2 - Álgebra y ecuaciones", [
            ("Resuelve: 3x + 4 = 19.", "x = 5."),
            ("Resuelve: 2(x - 3) = 10.", "x = 8."),
            ("Si y = 4x - 1, ¿cuánto vale y cuando x = 3?", "11."),
            ("¿Qué expresión representa “el doble de n disminuido en 7”?", "2n - 7."),
            ("Resuelve: 5x = 45.", "x = 9."),
            ("Resuelve: x/4 + 2 = 5.", "x = 12."),
            ("Un número más 8 es 21. ¿Cuál es el número?", "13."),
            ("¿Cuál es el valor de 2a + 3 si a = 6?", "15."),
            ("Resuelve: 7 - 2x = 1.", "x = 3."),
            ("¿Cuál es el siguiente término de 4, 7, 10, 13, ...?", "16."),
        ]),
        ("Taller 3 - Geometría y medición", [
            ("Un rectángulo mide 8 cm por 5 cm. ¿Cuál es su área?", "40 cm²."),
            ("Un cuadrado tiene lado de 6 cm. ¿Cuál es su perímetro?", "24 cm."),
            ("Un triángulo tiene base de 10 cm y altura de 4 cm. ¿Cuál es su área?", "20 cm²."),
            ("Dos ángulos de un triángulo miden 50° y 60°. ¿Cuánto mide el tercero?", "70°."),
            ("¿Cuántos grados suman los ángulos interiores de un cuadrilátero?", "360°."),
            ("Un círculo tiene radio de 3 cm. ¿Cuál es su diámetro?", "6 cm."),
            ("Un prisma mide 2 cm × 3 cm × 5 cm. ¿Cuál es su volumen?", "30 cm³."),
            ("Una distancia de 2,5 km equivale a ¿cuántos metros?", "2.500 metros."),
            ("¿Cuál es el complemento de un ángulo de 35°?", "55°."),
            ("Una caja cúbica tiene arista de 4 cm. ¿Cuál es su volumen?", "64 cm³."),
        ]),
        ("Taller 4 - Estadística y probabilidad", [
            ("¿Cuál es la media de 2, 4 y 9?", "5."),
            ("¿Cuál es la mediana de 3, 8, 1, 6 y 4?", "4."),
            ("¿Cuál es la moda de 2, 3, 3, 5 y 7?", "3."),
            ("Al lanzar una moneda equilibrada, ¿cuál es la probabilidad de cara?", "1/2."),
            ("Una bolsa tiene 3 bolas rojas y 2 azules. ¿Probabilidad de sacar una azul?", "2/5."),
            ("¿Cuál es el rango de 4, 9, 12 y 15?", "11."),
            ("En 20 lanzamientos, salió cara 12 veces. ¿Frecuencia relativa de cara?", "0,6."),
            ("Un dado justo tiene seis caras. ¿Probabilidad de obtener un 7?", "0."),
            ("Las notas son 3, 3, 4 y 5. ¿Cuál es la media?", "3,75."),
            ("Una ruleta tiene 8 sectores iguales y 2 son verdes. ¿Probabilidad de verde?", "1/4."),
        ]),
        ("Taller 5 - Funciones y variación", [
            ("Si f(x) = 2x + 3, ¿cuánto vale f(4)?", "11."),
            ("Una tarifa es $5.000 fijos más $2.000 por kilómetro. ¿Costo para 3 km?", "$11.000."),
            ("¿Cuál es la pendiente entre (0, 2) y (3, 8)?", "2."),
            ("Si y = 3x, ¿qué ocurre con y cuando x se duplica?", "y también se duplica."),
            ("Una máquina produce 12 piezas por hora. ¿Cuántas produce en 5 horas?", "60 piezas."),
            ("¿Cuál es la regla de la secuencia 5, 10, 15, 20, ...?", "Sumar 5 en cada paso."),
            ("Si g(x) = x², ¿cuánto vale g(5)?", "25."),
            ("En y = 4x - 2, ¿cuál es el valor inicial cuando x = 0?", "-2."),
            ("Un automóvil recorre 180 km en 3 horas a velocidad constante. ¿Velocidad?", "60 km/h."),
            ("Si h(x) = 10 - x, ¿cuánto vale h(6)?", "4."),
        ]),
    ],
    "Ciencias Naturales": [
        ("Taller 1 - Biología celular", [
            ("¿Qué estructura contiene la mayor parte del material genético de una célula eucariota?", "El núcleo."),
            ("¿Qué orgánulo produce gran parte de la energía utilizable de la célula?", "La mitocondria."),
            ("¿Qué estructura regula el intercambio entre la célula y su entorno?", "La membrana celular."),
            ("¿Qué proceso permite a las plantas fabricar glucosa usando luz?", "La fotosíntesis."),
            ("¿Qué molécula almacena la información hereditaria?", "El ADN."),
            ("¿Qué función cumplen principalmente los glóbulos rojos?", "Transportar oxígeno en la sangre."),
            ("¿Qué sistema del cuerpo coordina respuestas mediante señales nerviosas?", "El sistema nervioso."),
            ("¿Qué tipo de reproducción requiere la unión de gametos?", "La reproducción sexual."),
            ("¿Qué unidad básica forma los tejidos de los seres vivos?", "La célula."),
            ("¿Qué función cumplen las raíces de muchas plantas?", "Absorber agua y minerales y fijar la planta."),
        ]),
        ("Taller 2 - Ecología y ambiente", [
            ("En una cadena alimentaria, ¿qué organismo produce su propio alimento usando energía solar?", "El productor."),
            ("¿Qué nombre recibe el conjunto de seres vivos y su ambiente físico?", "Ecosistema."),
            ("¿Qué proceso devuelve vapor de agua desde las plantas a la atmósfera?", "La transpiración."),
            ("¿Qué ocurre con la energía disponible al avanzar entre niveles tróficos?", "Disminuye."),
            ("¿Qué relación beneficia a dos especies que interactúan?", "Mutualismo."),
            ("¿Qué gas aumenta principalmente por la quema de combustibles fósiles y contribuye al calentamiento?", "Dióxido de carbono."),
            ("¿Qué práctica convierte residuos en materiales que pueden volver a usarse?", "Reciclaje."),
            ("¿Qué recurso natural se renueva por el ciclo del agua, aunque puede contaminarse?", "El agua."),
            ("¿Qué efecto puede tener la deforestación sobre el suelo?", "Aumentar la erosión."),
            ("¿Qué organismos descomponen restos y reciclan nutrientes en un ecosistema?", "Hongos y bacterias."),
        ]),
        ("Taller 3 - Química cotidiana", [
            ("¿Cuál es el símbolo químico del oxígeno?", "O."),
            ("¿Qué indica un pH menor que 7 en una disolución acuosa?", "Que es ácida."),
            ("¿Qué partículas tienen carga eléctrica negativa?", "Los electrones."),
            ("¿Qué cambio de estado ocurre cuando el hielo se vuelve agua líquida?", "Fusión."),
            ("¿Qué sustancia se obtiene al combinar químicamente hidrógeno y oxígeno en proporción adecuada?", "Agua."),
            ("¿Qué método separa un sólido insoluble de un líquido mediante un filtro?", "Filtración."),
            ("¿Qué representa el número atómico de un elemento?", "La cantidad de protones en su núcleo."),
            ("¿Qué tipo de mezcla tiene composición uniforme a simple vista?", "Una mezcla homogénea."),
            ("¿Qué ocurre con las partículas cuando una sustancia se calienta?", "Aumenta su energía cinética promedio."),
            ("¿Qué gas se forma comúnmente cuando un ácido reacciona con un carbonato?", "Dióxido de carbono."),
        ]),
        ("Taller 4 - Física y energía", [
            ("¿Cuál es la unidad de fuerza en el Sistema Internacional?", "El newton."),
            ("¿Qué relación describe la velocidad?", "Distancia recorrida dividida por el tiempo."),
            ("¿Qué fuerza atrae los objetos hacia la Tierra?", "La gravedad."),
            ("¿En qué unidad se mide la corriente eléctrica?", "En amperios."),
            ("¿Qué forma de energía tiene un objeto por estar en movimiento?", "Energía cinética."),
            ("¿Qué ocurre con la luz al rebotar en una superficie?", "Reflexión."),
            ("¿Qué material permite con facilidad el paso de corriente eléctrica?", "Un conductor."),
            ("¿Qué transferencia de calor ocurre principalmente por el movimiento de un fluido?", "Convección."),
            ("¿Cuál es la unidad de potencia?", "El vatio."),
            ("¿Qué ley relaciona voltaje, corriente y resistencia en un circuito?", "La ley de Ohm."),
        ]),
        ("Taller 5 - Ciencia y salud", [
            ("¿Cuál es el primer paso para investigar un fenómeno de forma sistemática?", "Observar y formular una pregunta."),
            ("¿Qué variable modifica deliberadamente quien realiza un experimento?", "La variable independiente."),
            ("¿Por qué se repite un experimento?", "Para comprobar la consistencia de los resultados."),
            ("¿Qué grupo sirve como referencia para comparar un tratamiento experimental?", "El grupo de control."),
            ("¿Qué sistema protege al cuerpo frente a muchos agentes infecciosos?", "El sistema inmunitario."),
            ("¿Qué nutriente es la principal fuente inmediata de energía del organismo?", "Los carbohidratos."),
            ("¿Qué medida reduce la propagación de microorganismos en las manos?", "Lavarlas con agua y jabón."),
            ("¿Qué debe hacer una hipótesis científica frente a la evidencia?", "Poder ponerse a prueba y revisarse."),
            ("¿Qué órgano bombea la sangre por el cuerpo?", "El corazón."),
            ("¿Qué tipo de datos se expresan con números y mediciones?", "Datos cuantitativos."),
        ]),
    ],
    "Sociales y Ciudadanas": [
        ("Taller 1 - Historia de Colombia", [
            ("¿En qué año ocurrió el grito de independencia del 20 de julio en Santa Fe?", "1810."),
            ("¿Qué proceso histórico terminó con la disolución de la Gran Colombia?", "La separación de sus territorios en repúblicas independientes."),
            ("¿Qué nombre recibe el período de enfrentamientos entre liberales y conservadores iniciado en 1948?", "La Violencia."),
            ("¿Qué actividad económica fue central en la colonización antioqueña del siglo XIX?", "El cultivo del café."),
            ("¿Qué cambio político introdujo la Constitución colombiana de 1991?", "Amplió el reconocimiento de derechos y la participación ciudadana."),
            ("¿Qué pueblo habitaba gran parte de la región muisca antes de la conquista española?", "El pueblo muisca."),
            ("¿Qué acontecimiento se conmemora el 20 de julio en Colombia?", "El inicio del proceso de independencia de 1810."),
            ("¿Qué estableció la ley de libertad de los esclavos promulgada en Colombia en 1851?", "La eliminación legal de la esclavitud."),
            ("¿Qué tipo de fuente es una carta escrita durante un acontecimiento histórico?", "Una fuente primaria."),
            ("¿Por qué es importante contrastar versiones de un hecho histórico?", "Para reconocer perspectivas y construir una explicación mejor sustentada."),
        ]),
        ("Taller 2 - Geografía y territorio", [
            ("¿Qué cordillera atraviesa Colombia y se divide en tres ramales andinos?", "La cordillera de los Andes."),
            ("¿Qué océanos tienen costa en Colombia?", "El Pacífico y el Atlántico, a través del mar Caribe."),
            ("¿Qué río es uno de los principales ejes fluviales del centro del país?", "El río Magdalena."),
            ("¿Qué región natural colombiana se caracteriza por extensas llanuras orientales?", "La Orinoquía."),
            ("¿Qué es una cuenca hidrográfica?", "El territorio cuyas aguas drenan hacia un mismo río o cuerpo de agua."),
            ("¿Qué factor explica que las zonas altas tengan temperaturas más bajas?", "La altitud."),
            ("¿Qué región de Colombia incluye selvas húmedas y la costa del Pacífico?", "La región Pacífica."),
            ("¿Qué efecto puede generar la urbanización sin planeación sobre los humedales?", "Su reducción o deterioro."),
            ("¿Qué representa un mapa temático?", "La distribución espacial de un tema específico."),
            ("¿Qué actividad aprovecha de forma directa la fertilidad del suelo para producir alimentos?", "La agricultura."),
        ]),
        ("Taller 3 - Democracia y Constitución", [
            ("En una democracia, ¿quién es el titular de la soberanía según la Constitución colombiana?", "El pueblo."),
            ("¿Qué rama del poder público administra justicia en Colombia?", "La rama judicial."),
            ("¿Qué mecanismo permite a una persona pedir protección inmediata de un derecho fundamental?", "La acción de tutela."),
            ("¿Qué función principal cumple el Congreso de la República?", "Expedir leyes y ejercer control político."),
            ("¿Qué principio exige que las autoridades actúen conforme a las normas?", "El principio de legalidad."),
            ("¿Qué mecanismo permite a los ciudadanos elegir representantes mediante votación?", "El sufragio."),
            ("¿Qué derecho protege la posibilidad de expresar ideas sin censura previa, dentro de la ley?", "La libertad de expresión."),
            ("¿Qué característica debe tener una elección democrática?", "Ser periódica, libre y con voto secreto."),
            ("¿Qué deber ciudadano ayuda a financiar servicios públicos y programas estatales?", "Pagar los impuestos establecidos por la ley."),
            ("¿Qué entidad organiza las elecciones y lleva el registro civil en Colombia?", "La Registraduría Nacional del Estado Civil."),
        ]),
        ("Taller 4 - Economía y ciudadanía", [
            ("¿Qué describe la inflación?", "El aumento general y sostenido de los precios."),
            ("Si la demanda aumenta y la oferta permanece igual, ¿qué presión suele aparecer sobre el precio?", "Una presión al alza."),
            ("¿Qué es el costo de oportunidad?", "El valor de la mejor alternativa a la que se renuncia."),
            ("¿Qué función cumple un presupuesto familiar?", "Organizar ingresos y gastos previstos."),
            ("¿Qué significa ahorrar?", "Reservar parte del ingreso para usarla después."),
            ("¿Qué es un impuesto?", "Un pago obligatorio establecido por el Estado para financiar sus funciones."),
            ("¿Qué ocurre cuando una persona gasta persistentemente más de lo que recibe?", "Puede acumular deudas."),
            ("¿Qué se intercambia en un mercado?", "Bienes y servicios entre compradores y vendedores."),
            ("¿Qué indicador expresa el valor total de bienes y servicios finales producidos en un país durante un período?", "El producto interno bruto."),
            ("¿Qué decisión de consumo ayuda a evitar el sobreendeudamiento?", "Comparar ingresos, gastos y capacidad de pago antes de comprar."),
        ]),
        ("Taller 5 - Convivencia y fuentes", [
            ("Dos grupos discrepan sobre el uso de un espacio común. ¿Qué acción favorece una solución pacífica?", "Escuchar las necesidades y acordar reglas compartidas."),
            ("¿Qué significa participar en una veeduría ciudadana?", "Hacer seguimiento ciudadano a la gestión pública."),
            ("¿Qué dato ayuda a evaluar la confiabilidad de una publicación digital?", "La autoría y las fuentes que cita."),
            ("¿Qué es discriminación?", "Tratar injustamente a una persona por una característica o condición."),
            ("¿Qué principio guía la resolución de conflictos mediante el diálogo?", "Reconocer a las partes y buscar acuerdos."),
            ("Un informe público no indica fecha ni autor. ¿Qué debe hacerse antes de usarlo como evidencia?", "Verificar su origen y corroborarlo con otras fuentes."),
            ("¿Qué busca una política pública?", "Atender una necesidad colectiva mediante acciones institucionales."),
            ("¿Qué implica respetar la diversidad cultural?", "Reconocer distintas identidades y proteger la igualdad de derechos."),
            ("¿Qué permite una consulta popular?", "Que la ciudadanía se pronuncie directamente sobre una pregunta de interés público."),
            ("¿Qué acción fortalece la transparencia de una institución?", "Publicar información clara sobre sus decisiones y recursos."),
        ]),
    ],
    "Inglés": [
        ("Taller 1 - Vocabulary in context", [
            ("Choose the word that means the opposite of “early”.", "late"),
            ("In “She is very kind to new students”, what does “kind” mean?", "friendly and helpful"),
            ("Choose the correct word: “I need an ___ because it is cold.”", "jacket"),
            ("What is the plural of “child”?", "children"),
            ("A “library” is a place where people can…", "read or borrow books"),
            ("Choose the opposite of “expensive”.", "cheap"),
            ("What does “quiet” mean?", "making little or no noise"),
            ("Complete the category: apple, banana, orange are…", "fruit"),
            ("Which word describes a person who teaches students?", "teacher"),
            ("What does “borrow” mean?", "to take something temporarily and return it"),
        ]),
        ("Taller 2 - Grammar in context", [
            ("Complete: “She ___ to school every day.”", "goes"),
            ("Complete: “They ___ playing football now.”", "are"),
            ("Choose the past form: “Yesterday, we ___ a film.”", "watched"),
            ("Complete: “There ___ a book on the table.”", "is"),
            ("Choose the correct article: “He is ___ honest person.”", "an"),
            ("Complete: “I have lived here ___ 2020.”", "since"),
            ("Choose the comparative: “This road is ___ than that one.”", "longer"),
            ("Complete: “You ___ wear a helmet when riding a bike.”", "should"),
            ("Choose the correct pronoun: “Maria and ___ are classmates.”", "I"),
            ("Complete: “If it rains, we ___ at home.”", "will stay"),
        ]),
        ("Taller 3 - Reading comprehension", [
            ("Read: “Tom takes the bus at seven because his school is far away.” Why does Tom take the bus?", "His school is far away."),
            ("Read: “The shop closes on Sundays but opens at eight on Monday.” When does it open after Sunday?", "On Monday at eight."),
            ("Read: “Anna planted tomatoes in March and watered them every day.” What did Anna grow?", "Tomatoes."),
            ("Read: “The museum was free, so the family did not buy tickets.” Why did they pay nothing?", "Admission was free."),
            ("Read: “Ben missed the train, so he called his manager.” What happened first?", "Ben missed the train."),
            ("Read: “Lina prefers tea because coffee keeps her awake at night.” Why does Lina choose tea?", "Coffee affects her sleep."),
            ("Read: “The library lends books for two weeks.” How long may a book be borrowed?", "Two weeks."),
            ("Read: “It was sunny in the morning, but it rained in the afternoon.” What was the weather later?", "Rainy."),
            ("Read: “Sam saved money for three months and bought a bicycle.” What was Sam’s goal?", "To buy a bicycle."),
            ("Read: “The sign says ‘Keep off the grass.’ What should visitors do?", "Stay off the grass."),
        ]),
        ("Taller 4 - Everyday communication", [
            ("Someone says “Thank you for your help.” What is a polite reply?", "You’re welcome."),
            ("You did not hear a question. What can you say politely?", "Could you repeat that, please?"),
            ("How do you ask for the location of the nearest pharmacy?", "Where is the nearest pharmacy?"),
            ("A friend says “I’m sorry I’m late.” What is a suitable response?", "That’s all right."),
            ("How do you ask for the price of a shirt?", "How much is this shirt?"),
            ("You want to order water in a café. What can you say?", "Could I have some water, please?"),
            ("How do you offer help to someone carrying boxes?", "Can I help you?"),
            ("Someone asks “Would you like some tea?” and you accept. What do you say?", "Yes, please."),
            ("How do you ask permission to open a window?", "May I open the window?"),
            ("A person says “Have a nice weekend!” What is a friendly reply?", "Thanks, you too!"),
        ]),
        ("Taller 5 - English usage", [
            ("Choose the correct question: asking about a person's name.", "What is your name?"),
            ("Complete the direction: “Turn left ___ you reach the bank.”", "when"),
            ("Which sentence describes a habit?", "I walk to work every morning."),
            ("Complete: “The meeting starts ___ 9:30.”", "at"),
            ("Choose the correct sentence in the present continuous.", "They are studying for the exam."),
            ("What does the notice “No entry” mean?", "You must not go in."),
            ("Complete: “I am interested ___ science.”", "in"),
            ("Choose the correct negative form: “He ___ like coffee.”", "does not"),
            ("Which expression asks someone to wait briefly?", "Just a moment, please."),
            ("Complete: “We went to the park ___ Sunday.”", "on"),
        ]),
    ],
}


def validar_contenido():
    if set(TALLERES) != {
        "Lectura Crítica",
        "Matemáticas",
        "Ciencias Naturales",
        "Sociales y Ciudadanas",
        "Inglés",
    }:
        raise ValueError("El contenido debe cubrir las cinco áreas del proyecto.")

    total = 0
    for area, talleres in TALLERES.items():
        if len(talleres) != 5:
            raise ValueError(f"{area}: se esperaban exactamente cinco talleres.")
        nombres = set()
        for modulo, preguntas in talleres:
            if modulo in nombres or not modulo.startswith("Taller "):
                raise ValueError(f"{area}: nombre de taller inválido o repetido: {modulo}")
            nombres.add(modulo)
            if len(preguntas) != 10:
                raise ValueError(f"{modulo}: se esperaban exactamente diez preguntas.")
            respuestas = [respuesta for _, respuesta in preguntas]
            if len(set(respuestas)) != len(respuestas):
                raise ValueError(f"{modulo}: las respuestas correctas deben ser distintas.")
            if len({pregunta for pregunta, _ in preguntas}) != 10:
                raise ValueError(f"{modulo}: hay enunciados repetidos.")
            if any(not pregunta.strip() or not respuesta.strip() for pregunta, respuesta in preguntas):
                raise ValueError(f"{modulo}: hay preguntas o respuestas vacías.")
            for posicion in range(10):
                opciones = opciones_para(area, modulo, posicion, preguntas)
                if len(opciones) != 4 or sum(correcta for _, correcta in opciones) != 1:
                    raise ValueError(f"{modulo}: debe haber cuatro opciones y una correcta.")
            total += len(preguntas)
    return total


def opciones_para(area, modulo, posicion, preguntas):
    correcta = preguntas[posicion][1]
    distractores = []
    for salto in (2, 5, 7):
        opcion = preguntas[(posicion + salto) % len(preguntas)][1]
        if opcion != correcta and opcion not in distractores:
            distractores.append(opcion)
    if len(distractores) != 3:
        raise ValueError(f"No se pudieron crear cuatro opciones distintas para {modulo}.")

    opciones = [(correcta, 1)] + [(texto, 0) for texto in distractores]
    random.Random(f"{area}:{modulo}:{posicion}").shuffle(opciones)
    return opciones


def cargar():
    total = validar_contenido()
    from db import conectar

    db = conectar()
    insertadas = 0
    existentes = 0
    numeros = {}
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id_area, nombre_area FROM areas")
            areas = {fila["nombre_area"]: fila["id_area"] for fila in cursor.fetchall()}
            faltantes = sorted(set(TALLERES) - set(areas))
            if faltantes:
                raise RuntimeError(
                    "Faltan estas áreas en la base de datos: " + ", ".join(faltantes)
                )

            for nombre_area, talleres in TALLERES.items():
                id_area = areas[nombre_area]
                cursor.execute(
                    "SELECT COALESCE(MAX(numero_pregunta), 0) AS maximo "
                    "FROM preguntas WHERE id_area = %s",
                    (id_area,),
                )
                siguiente = int(cursor.fetchone()["maximo"])

                for modulo, preguntas in talleres:
                    for posicion, (enunciado, correcta) in enumerate(preguntas):
                        cursor.execute(
                            """
                            SELECT id_pregunta FROM preguntas
                            WHERE id_area = %s AND modulo = %s AND enunciado = %s
                            """,
                            (id_area, modulo, enunciado),
                        )
                        encontrada = cursor.fetchone()
                        if encontrada:
                            cursor.execute(
                                """
                                SELECT COUNT(*) AS total,
                                       SUM(es_correcta) AS correctas
                                FROM opciones WHERE id_pregunta = %s
                                """,
                                (encontrada["id_pregunta"],),
                            )
                            opciones_actuales = cursor.fetchone()
                            if int(opciones_actuales["total"]) != 4 or int(
                                opciones_actuales["correctas"] or 0
                            ) != 1:
                                raise RuntimeError(
                                    f"La pregunta existente está incompleta: {enunciado}"
                                )
                            existentes += 1
                            continue

                        siguiente += 1
                        cursor.execute(
                            """
                            INSERT INTO preguntas
                                (id_area, numero_pregunta, modulo, tema,
                                 enunciado, retroalimentacion)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (
                                id_area,
                                siguiente,
                                modulo,
                                modulo,
                                enunciado,
                                f"La respuesta correcta es: {correcta}",
                            ),
                        )
                        id_pregunta = cursor.lastrowid
                        for letra, (texto_opcion, es_correcta) in zip(
                            "ABCD", opciones_para(nombre_area, modulo, posicion, preguntas)
                        ):
                            cursor.execute(
                                """
                                INSERT INTO opciones
                                    (id_pregunta, letra, texto_opcion, es_correcta)
                                VALUES (%s, %s, %s, %s)
                                """,
                                (id_pregunta, letra, texto_opcion, es_correcta),
                            )
                        insertadas += 1

                numeros[nombre_area] = siguiente

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(
        f"Contenido verificado: {total} preguntas en 25 talleres. "
        f"Insertadas: {insertadas}; ya existentes: {existentes}."
    )
    for nombre_area, maximo in numeros.items():
        print(f"{nombre_area}: {maximo} preguntas numeradas en total.")


if __name__ == "__main__":
    if "--validar" in sys.argv:
        print(f"Contenido válido: {validar_contenido()} preguntas en 25 talleres.")
    else:
        cargar()
