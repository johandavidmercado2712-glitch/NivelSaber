"""
Práctica del estudiante (exige sesión y rol estudiante):

    GET  /api/areas          -> áreas con cantidad de talleres y preguntas
    GET  /api/talleres       -> talleres disponibles para un área
    GET  /api/preguntas      -> preguntas y opciones de un taller
    POST /api/respuestas     -> califica, guarda respuestas y crea el resultado
    GET  /api/resultados     -> última práctica, desempeño por área y errores
    GET  /api/estadisticas   -> resumen global para la ficha de perfil
    GET  /api/historial      -> todas las prácticas + desempeño por tema
    GET  /api/historial/<id> -> detalle de una práctica concreta
"""

import logging

from flask import Blueprint, jsonify, request

from ayudas import (SQL_BANCO, armar_banco, datos, entero,
                    requiere_estudiante, requiere_sesion)
from db import consultar, get_db

logger = logging.getLogger(__name__)

bp = Blueprint("practica", __name__, url_prefix="/api")


# ------------------------------------------------------------------
# Banco de preguntas
# ------------------------------------------------------------------
@bp.get("/areas")
def listar_areas():
    usuario, error = requiere_sesion()
    if error:
        return error

    # Sólo lectura: consultar() trae las filas sin repetir el patrón
    # "db = get_db() + with db.cursor()" de las rutas que escriben.
    filas = consultar(
        """
        SELECT a.id_area, a.nombre_area,
               COUNT(p.id_pregunta) AS preguntas,
               COUNT(DISTINCT CASE
                   WHEN p.modulo LIKE 'Taller %%' THEN p.modulo
               END) AS talleres,
               SUM(CASE
                   WHEN p.id_pregunta IS NOT NULL
                    AND (p.modulo IS NULL OR p.modulo NOT LIKE 'Taller %%')
                   THEN 1 ELSE 0
               END) AS preguntas_anteriores
        FROM areas a
        LEFT JOIN preguntas p ON p.id_area = a.id_area
        GROUP BY a.id_area, a.nombre_area
        ORDER BY a.id_area
        """
    )

    return jsonify(ok=True, areas=filas)


@bp.get("/talleres")
def listar_talleres():
    usuario, error = requiere_estudiante()
    if error:
        return error

    id_area = entero(request.args.get("area"))
    if not id_area:
        return jsonify(ok=False, error="Falta el parametro area."), 400

    filas = consultar(
        """
        SELECT CASE WHEN p.modulo LIKE 'Taller %%'
                    THEN p.modulo ELSE '__banco_anterior__' END AS id_taller,
               CASE WHEN p.modulo LIKE 'Taller %%'
                    THEN p.modulo ELSE 'Preguntas anteriores' END AS nombre_taller,
               COUNT(*) AS preguntas
        FROM preguntas p
        WHERE p.id_area = %s
        GROUP BY id_taller, nombre_taller
        ORDER BY CASE WHEN id_taller = '__banco_anterior__' THEN 1 ELSE 0 END,
                 nombre_taller
        """,
        (id_area,),
    )

    return jsonify(ok=True, id_area=id_area, talleres=filas)


def _consultar_banco(cursor, id_area, id_taller=None):
    consulta = SQL_BANCO
    parametros = [id_area]
    if id_taller == "__banco_anterior__":
        consulta = consulta.replace(
            "WHERE p.id_area = %s",
            "WHERE p.id_area = %s AND (p.modulo IS NULL OR p.modulo NOT LIKE 'Taller %%')",
        )
    elif id_taller:
        consulta = consulta.replace(
            "WHERE p.id_area = %s",
            "WHERE p.id_area = %s AND p.modulo = %s",
        )
        parametros.append(id_taller)

    cursor.execute(consulta, tuple(parametros))
    return cursor.fetchall()


@bp.get("/preguntas")
def listar_preguntas():
    usuario, error = requiere_estudiante()
    if error:
        return error

    id_area = entero(request.args.get("area"))
    id_taller = request.args.get("taller", "").strip()
    if not id_area:
        return jsonify(ok=False, error="Falta el parametro area."), 400

    with get_db().cursor() as cursor:
        filas = _consultar_banco(cursor, id_area, id_taller or None)

    banco = armar_banco(filas)
    if not banco:
        return jsonify(ok=False, error="Ese taller no tiene preguntas cargadas."), 404

    # es_correcta se elimina: el cliente no debe poder hacer trampa.
    publico = [
        {
            "id_pregunta": p["id_pregunta"],
            "numero": p["numero"],
            "modulo": p["modulo"],
            "tema": p["tema"],
            "enunciado": p["enunciado"],
            "opciones": [
                {"id_opcion": o["id_opcion"], "letra": o["letra"], "texto": o["texto"]}
                for o in p["opciones"]
            ],
        }
        for p in banco
    ]

    return jsonify(
        ok=True,
        id_area=id_area,
        id_taller=id_taller or None,
        preguntas=publico,
    )


# ------------------------------------------------------------------
# Práctica
# ------------------------------------------------------------------
@bp.post("/respuestas")
def guardar_respuestas():
    usuario, error = requiere_estudiante()
    if error:
        return error

    data = datos()
    id_area = entero(data.get("id_area"))
    id_taller = str(data.get("taller") or "").strip()
    brutas = data.get("respuestas")

    if not id_area:
        return jsonify(ok=False, error="Falta el area de la practica."), 400
    if not isinstance(brutas, list) or not brutas:
        return jsonify(ok=False, error="No se recibieron respuestas."), 400

    elegidas = {}
    for item in brutas:
        if not isinstance(item, dict):
            return jsonify(ok=False, error="Respuesta mal formada."), 400
        id_pregunta = entero(item.get("id_pregunta"))
        id_opcion = entero(item.get("id_opcion"))
        if not id_pregunta or not id_opcion:
            return jsonify(ok=False, error="Respuesta mal formada."), 400
        if id_pregunta in elegidas:
            return jsonify(ok=False, error="Una pregunta fue respondida dos veces."), 400
        elegidas[id_pregunta] = id_opcion

    db = get_db()
    with db.cursor() as cursor:
        filas = _consultar_banco(cursor, id_area, id_taller or None)

    banco = armar_banco(filas)
    if not banco:
        return jsonify(ok=False, error="Ese taller no tiene preguntas cargadas."), 404

    preguntas_ids = {p["id_pregunta"] for p in banco}
    if set(elegidas) != preguntas_ids:
        faltan = sorted(preguntas_ids - set(elegidas))
        return (
            jsonify(
                ok=False,
                error="Debes responder todas las preguntas antes de enviar.",
                faltantes=faltan,
            ),
            400,
        )

    # Se recorre el banco armado para validar y calificar en memoria.
    correctas = 0
    detalle = []
    for pregunta in banco:
        opciones = {o["id_opcion"]: o for o in pregunta["opciones"]}
        elegida = opciones.get(elegidas[pregunta["id_pregunta"]])
        if elegida is None:
            return jsonify(ok=False, error="La opcion elegida no pertenece a la pregunta."), 400

        acerto = elegida["correcta"]
        if acerto:
            correctas += 1

        correcta = next(o for o in pregunta["opciones"] if o["correcta"])
        detalle.append(
            {
                "id_pregunta": pregunta["id_pregunta"],
                "numero": pregunta["numero"],
                "enunciado": pregunta["enunciado"],
                "retroalimentacion": pregunta["retroalimentacion"],
                "elegida": {"letra": elegida["letra"], "texto": elegida["texto"]},
                "correcta": {"letra": correcta["letra"], "texto": correcta["texto"]},
                "es_correcta": acerto,
            }
        )

    total = len(banco)
    incorrectas = total - correctas
    porcentaje = round(correctas * 100.0 / total, 2)

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO resultados
                    (id_usuario, id_area, preguntas_totales,
                     respuestas_correctas, respuestas_incorrectas, porcentaje)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (usuario["id"], id_area, total, correctas, incorrectas, porcentaje),
            )
            id_resultado = cursor.lastrowid

            for id_pregunta, id_opcion in elegidas.items():
                detalle_pregunta = next(d for d in detalle if d["id_pregunta"] == id_pregunta)
                cursor.execute(
                    """
                    INSERT INTO respuestas_usuario
                        (id_usuario, id_pregunta, id_opcion, es_correcta, id_resultado)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        usuario["id"],
                        id_pregunta,
                        id_opcion,
                        1 if detalle_pregunta["es_correcta"] else 0,
                        id_resultado,
                    ),
                )
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error al guardar la practica")
        return jsonify(ok=False, error="No se pudo guardar la practica."), 500

    return (
        jsonify(
            ok=True,
            resultado={
                "id_resultado": id_resultado,
                "id_area": id_area,
                "nombre_taller": (
                    "Preguntas anteriores"
                    if id_taller == "__banco_anterior__"
                    else id_taller or "Práctica general"
                ),
                "preguntas_totales": total,
                "respuestas_correctas": correctas,
                "respuestas_incorrectas": incorrectas,
                "porcentaje": porcentaje,
            },
            detalle=detalle,
        ),
        201,
    )


@bp.get("/resultados")
def ver_resultados():
    usuario, error = requiere_estudiante()
    if error:
        return error

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT r.id_resultado, r.preguntas_totales, r.respuestas_correctas,
                   r.respuestas_incorrectas, r.porcentaje, r.fecha_practica,
                   a.id_area, a.nombre_area,
                   (SELECT CASE
                       WHEN COUNT(DISTINCT p.modulo) = 1 THEN MAX(p.modulo)
                       WHEN COUNT(DISTINCT p.modulo) = 0 THEN 'Preguntas anteriores'
                       ELSE 'Práctica mixta'
                   END
                    FROM respuestas_usuario ru
                    JOIN preguntas p ON p.id_pregunta = ru.id_pregunta
                    WHERE ru.id_resultado = r.id_resultado) AS nombre_taller
            FROM resultados r
            JOIN areas a ON a.id_area = r.id_area
            WHERE r.id_usuario = %s
            ORDER BY r.id_resultado DESC
            LIMIT 1
            """,
            (usuario["id"],),
        )
        ultima = cursor.fetchone()

        if not ultima:
            return jsonify(ok=True, hay_datos=False)

        cursor.execute(
            """
            SELECT a.id_area, a.nombre_area,
                   ROUND(AVG(r.porcentaje))       AS porcentaje,
                   SUM(r.respuestas_correctas)    AS correctas,
                   SUM(r.preguntas_totales)       AS preguntas,
                   COUNT(*)                       AS practicas
            FROM resultados r
            JOIN areas a ON a.id_area = r.id_area
            WHERE r.id_usuario = %s
            GROUP BY a.id_area, a.nombre_area
            ORDER BY porcentaje DESC, a.nombre_area
            """,
            (usuario["id"],),
        )
        por_area = cursor.fetchall()

        cursor.execute(
            """
            SELECT ru.id_pregunta, p.numero_pregunta, p.modulo, p.tema,
                   p.enunciado, p.retroalimentacion,
                   elegida.texto_opcion  AS texto_elegida,
                   elegida.letra         AS letra_elegida,
                   correcta.texto_opcion AS texto_correcta,
                   correcta.letra        AS letra_correcta
            FROM respuestas_usuario ru
            JOIN preguntas p     ON p.id_pregunta  = ru.id_pregunta
            JOIN opciones elegida  ON elegida.id_opcion  = ru.id_opcion
            JOIN opciones correcta ON correcta.id_pregunta = ru.id_pregunta
                                  AND correcta.es_correcta = 1
            WHERE ru.id_resultado = %s AND ru.es_correcta = 0
            ORDER BY p.numero_pregunta
            """,
            (ultima["id_resultado"],),
        )
        incorrectas = cursor.fetchall()

    ultima["fecha_practica"] = str(ultima["fecha_practica"])
    ultima["porcentaje"] = float(ultima["porcentaje"])

    # SUM() y ROUND() llegan como Decimal; a la interfaz les llegan números.
    for fila in por_area:
        fila["porcentaje"] = int(fila["porcentaje"])
        fila["correctas"] = int(fila["correctas"])
        fila["preguntas"] = int(fila["preguntas"])
        fila["practicas"] = int(fila["practicas"])

    return jsonify(
        ok=True,
        hay_datos=True,
        ultima=ultima,
        por_area=por_area,
        incorrectas=incorrectas,
    )


@bp.get("/estadisticas")
def estadisticas():
    usuario, error = requiere_estudiante()
    if error:
        return error

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)                        AS practicas,
                   COUNT(DISTINCT id_area)         AS areas_completadas,
                   COALESCE(SUM(respuestas_correctas), 0) AS correctas,
                   COALESCE(SUM(preguntas_totales), 0)    AS preguntas
            FROM resultados
            WHERE id_usuario = %s
            """,
            (usuario["id"],),
        )
        resumen = cursor.fetchone()

        cursor.execute(
            """
            SELECT COUNT(*) AS respondidas, COALESCE(SUM(es_correcta), 0) AS acertadas
            FROM respuestas_usuario
            WHERE id_usuario = %s
            """,
            (usuario["id"],),
        )
        respuestas = cursor.fetchone()

    # COUNT() devuelve int, pero SUM() devuelve Decimal: se normalizan.
    preguntas = int(resumen["preguntas"] or 0)
    correctas = int(resumen["correctas"] or 0)
    precision = round(correctas * 100.0 / preguntas) if preguntas else None

    return jsonify(
        ok=True,
        estadisticas={
            "practicas": int(resumen["practicas"]),
            "areas_completadas": int(resumen["areas_completadas"]),
            "precision": precision,
            "preguntas_respondidas": int(respuestas["respondidas"]),
            "respuestas_acertadas": int(respuestas["acertadas"] or 0),
        },
    )


# ------------------------------------------------------------------
# Historial de practicas y desempeno por tema
# ------------------------------------------------------------------
@bp.get("/historial")
def historial():
    """Lista paginada de las practicas del usuario y su desempeno por tema."""
    usuario, error = requiere_estudiante()
    if error:
        return error

    por_pagina = entero(request.args.get("por_pagina")) or 10
    por_pagina = min(por_pagina, 50)
    area = entero(request.args.get("area"))

    filtros = "WHERE r.id_usuario = %s"
    params = [usuario["id"]]
    if area:
        filtros += " AND r.id_area = %s"
        params.append(area)

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM resultados r " + filtros, tuple(params))
        total = int(cursor.fetchone()["total"])

        paginas = max(1, -(-total // por_pagina))
        pagina = entero(request.args.get("pagina")) or 1
        pagina = min(pagina, paginas)

        cursor.execute(
            """
            SELECT r.id_resultado, r.id_area, r.preguntas_totales,
                   r.respuestas_correctas, r.respuestas_incorrectas,
                   r.porcentaje, r.fecha_practica, a.nombre_area,
                   (SELECT CASE
                       WHEN COUNT(DISTINCT p.modulo) = 1 THEN MAX(p.modulo)
                       WHEN COUNT(DISTINCT p.modulo) = 0 THEN 'Preguntas anteriores'
                       ELSE 'Práctica mixta'
                   END
                    FROM respuestas_usuario ru
                    JOIN preguntas p ON p.id_pregunta = ru.id_pregunta
                    WHERE ru.id_resultado = r.id_resultado) AS nombre_taller
            FROM resultados r
            JOIN areas a ON a.id_area = r.id_area
            """
            + filtros
            + """
            ORDER BY r.fecha_practica DESC, r.id_resultado DESC
            LIMIT %s OFFSET %s
            """,
            tuple(params) + (por_pagina, (pagina - 1) * por_pagina),
        )
        filas = cursor.fetchall()

        cursor.execute(
            """
            SELECT a.id_area, a.nombre_area
            FROM areas a
            WHERE EXISTS (SELECT 1 FROM resultados r
                          WHERE r.id_area = a.id_area AND r.id_usuario = %s)
            ORDER BY a.nombre_area
            """,
            (usuario["id"],),
        )
        areas = cursor.fetchall()

        cursor.execute(
            """
            SELECT p.modulo, p.tema,
                   COUNT(*) AS respondidas,
                   ROUND(SUM(ru.es_correcta) * 100.0 / COUNT(*)) AS `precision`
            FROM respuestas_usuario ru
            JOIN preguntas p ON p.id_pregunta = ru.id_pregunta
            WHERE ru.id_usuario = %s
            GROUP BY p.modulo, p.tema
            ORDER BY `precision` ASC, respondidas DESC, p.tema
            """,
            (usuario["id"],),
        )
        temas = cursor.fetchall()

    # datetime y Decimal no son serializables: se convierten aqui.
    for fila in filas:
        fila["fecha_practica"] = str(fila["fecha_practica"])
        fila["porcentaje"] = float(fila["porcentaje"])
        fila["preguntas_totales"] = int(fila["preguntas_totales"])
        fila["respuestas_correctas"] = int(fila["respuestas_correctas"])
        fila["respuestas_incorrectas"] = int(fila["respuestas_incorrectas"])

    for fila in temas:
        fila["precision"] = int(fila["precision"] or 0)
        fila["respondidas"] = int(fila["respondidas"])
        fila["modulo"] = fila["modulo"] or "Sin modulo"
        fila["tema"] = fila["tema"] or "Sin tema"

    return jsonify(
        ok=True,
        historial=filas,
        total=total,
        pagina=pagina,
        paginas=paginas,
        por_pagina=por_pagina,
        areas=areas,
        temas=temas,
    )


@bp.get("/historial/<int:id_resultado>")
def historial_detalle(id_resultado):
    """Detalle de una practica. Sólo se puede leer la propia: si no es
    tuya o no existe se responde 404 para no delatar a otros usuarios."""
    usuario, error = requiere_estudiante()
    if error:
        return error

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT r.id_resultado, r.id_area, r.preguntas_totales,
                   r.respuestas_correctas, r.respuestas_incorrectas,
                   r.porcentaje, r.fecha_practica, a.nombre_area,
                   (SELECT CASE
                       WHEN COUNT(DISTINCT p.modulo) = 1 THEN MAX(p.modulo)
                       WHEN COUNT(DISTINCT p.modulo) = 0 THEN 'Preguntas anteriores'
                       ELSE 'Práctica mixta'
                   END
                    FROM respuestas_usuario ru
                    JOIN preguntas p ON p.id_pregunta = ru.id_pregunta
                    WHERE ru.id_resultado = r.id_resultado) AS nombre_taller
            FROM resultados r
            JOIN areas a ON a.id_area = r.id_area
            WHERE r.id_resultado = %s AND r.id_usuario = %s
            """,
            (id_resultado, usuario["id"]),
        )
        practica = cursor.fetchone()
        if not practica:
            return jsonify(ok=False, error="Practica no encontrada."), 404

        cursor.execute(
            """
            SELECT ru.id_pregunta, ru.es_correcta,
                   p.numero_pregunta, p.modulo, p.tema,
                   p.enunciado, p.retroalimentacion,
                   elegida.letra         AS letra_elegida,
                   elegida.texto_opcion   AS texto_elegida,
                   correcta.letra         AS letra_correcta,
                   correcta.texto_opcion  AS texto_correcta
            FROM respuestas_usuario ru
            JOIN preguntas p         ON p.id_pregunta  = ru.id_pregunta
            JOIN opciones elegida     ON elegida.id_opcion  = ru.id_opcion
            JOIN opciones correcta    ON correcta.id_pregunta = ru.id_pregunta
                                    AND correcta.es_correcta = 1
            WHERE ru.id_resultado = %s AND ru.id_usuario = %s
            ORDER BY p.numero_pregunta
            """,
            (id_resultado, usuario["id"]),
        )
        respuestas = cursor.fetchall()

    practica["fecha_practica"] = str(practica["fecha_practica"])
    practica["porcentaje"] = float(practica["porcentaje"])
    practica["preguntas_totales"] = int(practica["preguntas_totales"])
    practica["respuestas_correctas"] = int(practica["respuestas_correctas"])
    practica["respuestas_incorrectas"] = int(practica["respuestas_incorrectas"])

    for fila in respuestas:
        fila["es_correcta"] = bool(fila["es_correcta"])

    return jsonify(ok=True, practica=practica, respuestas=respuestas)
