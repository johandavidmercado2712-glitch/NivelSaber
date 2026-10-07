"""
Funciones compartidas por todas las rutas (no son rutas en sí):

    datos() / texto() / entero()              -> leer y validar lo que llega
    requiere_sesion() / requiere_admin() /
    requiere_estudiante()                     -> quién puede entrar a cada zona
    SQL_BANCO + armar_banco()                 -> consultar el banco de preguntas
    guardar_opciones() / editar_opciones() /
    leer_pregunta()                           -> utilidades del formulario admin
    TIPOS_OBJETIVO + avance_usuario()         -> avance real de los objetivos
"""

from flask import jsonify, request, session

# Consulta base que trae cada pregunta junto con todas sus opciones.
# El orden se fija con FIELD() para que las letras salgan A, B, C, D.
SQL_BANCO = """
    SELECT p.id_pregunta, p.numero_pregunta, p.modulo, p.tema,
           p.enunciado, p.retroalimentacion,
           o.id_opcion, o.letra, o.texto_opcion, o.es_correcta
    FROM preguntas p
    JOIN opciones o ON o.id_pregunta = p.id_pregunta
    WHERE p.id_area = %s
    ORDER BY p.numero_pregunta, FIELD(o.letra, 'A', 'B', 'C', 'D', 'E', 'F')
"""


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def datos():
    """Acepta tanto application/json como application/x-www-form-urlencoded."""
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form


def texto(data, *claves):
    for clave in claves:
        valor = data.get(clave)
        if valor is not None:
            return str(valor).strip()
    return ""


def entero(valor):
    """Convierte a entero positivo o devuelve None."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return None
    return numero if numero > 0 else None


def requiere_sesion():
    """Devuelve (usuario, None) o (None, respuesta_401)."""
    usuario = session.get("usuario")
    if not usuario:
        return None, (jsonify(ok=False, error="Debes iniciar sesion."), 401)
    return usuario, None


def requiere_admin():
    """Igual que requiere_sesion, pero ademas exige rol 'admin'."""
    usuario, error = requiere_sesion()
    if error:
        return None, error
    if str(usuario.get("rol", "")).strip().lower() != "admin":
        return None, (jsonify(ok=False, error="Esta zona es solo del administrador."), 403)
    return usuario, None


def requiere_estudiante():
    """Limita las rutas de práctica y resultados a cuentas de estudiante."""
    usuario, error = requiere_sesion()
    if error:
        return None, error
    if str(usuario.get("rol", "")).strip().lower() != "estudiante":
        return None, (jsonify(ok=False, error="Esta zona es solo para estudiantes."), 403)
    return usuario, None


def guardar_opciones(cursor, id_pregunta, opciones):
    """Inserta las opciones asignando las letras A, B, C, D por orden."""
    letras = "ABCD"
    for posicion, opcion in enumerate(opciones):
        cursor.execute(
            """
            INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
            VALUES (%s, %s, %s, %s)
            """,
            (id_pregunta, letras[posicion], opcion["texto"], 1 if opcion["correcta"] else 0),
        )


class OpcionesEnUso(Exception):
    pass


def editar_opciones(cursor, id_pregunta, opciones):
    """Edita opciones conservando ids y bloqueando la pérdida de respuestas."""
    letras = "ABCD"
    cursor.execute(
        "SELECT id_opcion FROM opciones WHERE id_pregunta = %s ORDER BY letra",
        (id_pregunta,),
    )
    actuales = [fila["id_opcion"] for fila in cursor.fetchall()]
    conservadas = min(len(actuales), len(opciones))
    for posicion in range(conservadas):
        opcion = opciones[posicion]
        cursor.execute(
            """
            UPDATE opciones
            SET letra = %s, texto_opcion = %s, es_correcta = %s
            WHERE id_opcion = %s
            """,
            (letras[posicion], opcion["texto"],
             1 if opcion["correcta"] else 0, actuales[posicion]),
        )

    if len(opciones) < len(actuales):
        eliminadas = actuales[len(opciones):]
        marcadores = ", ".join(["%s"] * len(eliminadas))
        cursor.execute(
            "SELECT COUNT(*) AS total FROM respuestas_usuario "
            "WHERE id_opcion IN (" + marcadores + ")",
            tuple(eliminadas),
        )
        if cursor.fetchone()["total"]:
            raise OpcionesEnUso
        cursor.execute(
            "DELETE FROM opciones WHERE id_opcion IN (" + marcadores + ")",
            tuple(eliminadas),
        )
    elif len(opciones) > len(actuales):
        for posicion in range(len(actuales), len(opciones)):
            opcion = opciones[posicion]
            cursor.execute(
                """
                INSERT INTO opciones (id_pregunta, letra, texto_opcion, es_correcta)
                VALUES (%s, %s, %s, %s)
                """,
                (id_pregunta, letras[posicion], opcion["texto"],
                 1 if opcion["correcta"] else 0),
            )

def leer_pregunta(data):
    """Valida el formulario del admin. Devuelve (error, campos)."""
    enunciado = texto(data, "enunciado")
    opciones = data.get("opciones")

    if not enunciado:
        return "Escribe el enunciado de la pregunta.", None
    if not isinstance(opciones, list) or not 2 <= len(opciones) <= 4:
        return "La pregunta necesita entre 2 y 4 opciones.", None

    limpias = []
    correctas = 0
    for opcion in opciones:
        if not isinstance(opcion, dict):
            return "Opcion mal formada.", None
        texto_opcion = str(opcion.get("texto", "")).strip()
        if not texto_opcion:
            return "Escribe el texto de todas las opciones.", None
        es_correcta = bool(opcion.get("correcta"))
        correctas += 1 if es_correcta else 0
        limpias.append({"texto": texto_opcion, "correcta": es_correcta})
    if correctas != 1:
        return "Marca exactamente una opcion como correcta.", None

    campos = {
        "modulo": texto(data, "modulo") or "General",
        "tema": texto(data, "tema") or "General",
        "enunciado": enunciado,
        "retroalimentacion": texto(data, "retroalimentacion"),
        "opciones": limpias,
    }
    return None, campos


def armar_banco(filas):
    """Agrupa las filas de SQL_BANCO en preguntas con su lista de opciones."""
    banco = {}
    for fila in filas:
        pregunta = banco.setdefault(
            fila["id_pregunta"],
            {
                "id_pregunta": fila["id_pregunta"],
                "numero": fila["numero_pregunta"],
                "modulo": fila["modulo"],
                "tema": fila["tema"],
                "enunciado": fila["enunciado"],
                "retroalimentacion": fila["retroalimentacion"],
                "opciones": [],
            },
        )
        pregunta["opciones"].append(
            {
                "id_opcion": fila["id_opcion"],
                "letra": fila["letra"],
                "texto": fila["texto_opcion"],
                "correcta": bool(fila["es_correcta"]),
            }
        )
    return list(banco.values())


# Cada objetivo guarda sólo el tipo y la meta. El avance se calcula en
# cada petición con los datos reales de la cuenta, así un objetivo
# recién creado siempre empieza en 0 y nunca muestra progreso falso.
TIPOS_OBJETIVO = {
    "preguntas": "Completar {meta} preguntas",
    "practicas": "Hacer {meta} prácticas",
    "areas": "Practicar {meta} áreas distintas",
    "precision": "Subir mi precisión al {meta}%",
}


def avance_usuario(cursor, id_usuario):
    """Suma real de la cuenta: preguntas respondidas, prácticas, áreas
    distintas y precisión global."""
    cursor.execute(
        """
        SELECT COUNT(*)                      AS practicas,
               COUNT(DISTINCT id_area)       AS areas,
               COALESCE(SUM(respuestas_correctas), 0) AS correctas,
               COALESCE(SUM(preguntas_totales), 0)    AS preguntas_resultado
        FROM resultados
        WHERE id_usuario = %s
        """,
        (id_usuario,),
    )
    resumen = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*) AS respondidas, COALESCE(SUM(es_correcta), 0) AS acertadas
        FROM respuestas_usuario
        WHERE id_usuario = %s
        """,
        (id_usuario,),
    )
    respuestas = cursor.fetchone()

    preguntas = int(respuestas["respondidas"])
    acertadas = int(respuestas["acertadas"] or 0)
    return {
        "preguntas": preguntas,
        "practicas": int(resumen["practicas"]),
        "areas": int(resumen["areas"]),
        "precision": round(acertadas * 100.0 / preguntas) if preguntas else 0,
    }

