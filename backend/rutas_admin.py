"""
Administración (sólo usuarios con rol admin; sin él devuelve 403):

    GET    /api/admin/areas/<id>          -> detalle del área: banco, respuestas y prácticas
    POST   /api/admin/areas               -> crea un área
    PUT    /api/admin/areas/<id>          -> cambia el nombre de un área
    DELETE /api/admin/areas/<id>          -> borra áreas sin preguntas ni resultados
    GET    /api/admin/preguntas?area=<id> -> banco completo (con respuestas)
    POST   /api/admin/preguntas           -> crea una pregunta con opciones
    PUT    /api/admin/preguntas/<id>      -> edita una pregunta
    DELETE /api/admin/preguntas/<id>      -> borra una pregunta
    GET    /api/admin/usuarios            -> cuentas registradas con su actividad
"""

import logging

import pymysql
from flask import Blueprint, jsonify, request

from ayudas import (SQL_BANCO, OpcionesEnUso, armar_banco, datos,
                    editar_opciones, entero, guardar_opciones, leer_pregunta,
                    requiere_admin, texto)
from db import consultar, get_db

logger = logging.getLogger(__name__)

bp = Blueprint("admin", __name__, url_prefix="/api")


@bp.post("/admin/areas")
def admin_crear_area():
    usuario, error = requiere_admin()
    if error:
        return error

    nombre = texto(datos(), "nombre_area", "nombre")
    if not nombre:
        return jsonify(ok=False, error="Escribe el nombre del área."), 400
    if len(nombre) > 100:
        return jsonify(ok=False, error="El nombre del área no puede superar 100 caracteres."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO areas (nombre_area) VALUES (%s)", (nombre,))
            id_area = cursor.lastrowid
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        return jsonify(ok=False, error="Ya existe un área con ese nombre."), 409
    except Exception:
        db.rollback()
        logger.exception("Error al crear el area")
        return jsonify(ok=False, error="No se pudo crear el área."), 500

    return jsonify(ok=True, mensaje="Área creada.", id_area=id_area), 201


@bp.put("/admin/areas/<int:id_area>")
def admin_editar_area(id_area):
    usuario, error = requiere_admin()
    if error:
        return error

    nombre = texto(datos(), "nombre_area", "nombre")
    if not nombre:
        return jsonify(ok=False, error="Escribe el nombre del área."), 400
    if len(nombre) > 100:
        return jsonify(ok=False, error="El nombre del área no puede superar 100 caracteres."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id_area FROM areas WHERE id_area = %s", (id_area,))
            if not cursor.fetchone():
                return jsonify(ok=False, error="Esa área no existe."), 404
            cursor.execute(
                "UPDATE areas SET nombre_area = %s WHERE id_area = %s",
                (nombre, id_area),
            )
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        return jsonify(ok=False, error="Ya existe un área con ese nombre."), 409
    except Exception:
        db.rollback()
        logger.exception("Error al editar el area")
        return jsonify(ok=False, error="No se pudo editar el área."), 500

    return jsonify(ok=True, mensaje="Área actualizada.")


@bp.delete("/admin/areas/<int:id_area>")
def admin_borrar_area(id_area):
    usuario, error = requiere_admin()
    if error:
        return error

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id_area FROM areas WHERE id_area = %s", (id_area,))
            if not cursor.fetchone():
                return jsonify(ok=False, error="Esa área no existe."), 404

            cursor.execute(
                "SELECT (SELECT COUNT(*) FROM preguntas WHERE id_area = %s) AS preguntas, "
                "(SELECT COUNT(*) FROM resultados WHERE id_area = %s) AS resultados",
                (id_area, id_area),
            )
            dependencias = cursor.fetchone()
            if dependencias["preguntas"] or dependencias["resultados"]:
                return (
                    jsonify(
                        ok=False,
                        error="No se puede eliminar un área que tiene preguntas o resultados asociados.",
                    ),
                    409,
                )

            cursor.execute("DELETE FROM areas WHERE id_area = %s", (id_area,))
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        return (
            jsonify(ok=False, error="No se puede eliminar el área porque tiene información asociada."),
            409,
        )
    except Exception:
        db.rollback()
        logger.exception("Error al borrar el area")
        return jsonify(ok=False, error="No se pudo eliminar el área."), 500

    return jsonify(ok=True, mensaje="Área eliminada.")


@bp.get("/admin/areas/<int:id_area>")
def admin_detalle_area(id_area):
    """Detalle completo de un área para el panel: resumen general, banco de
    preguntas con todas sus opciones y cuántas respuestas recibió cada una."""
    usuario, error = requiere_admin()
    if error:
        return error

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id_area, nombre_area FROM areas WHERE id_area = %s",
            (id_area,),
        )
        area = cursor.fetchone()
        if not area:
            return jsonify(ok=False, error="Esa área no existe."), 404

        # Resumen general del área.
        cursor.execute(
            """
            SELECT (SELECT COUNT(*) FROM preguntas WHERE id_area = %s) AS preguntas,
                   (SELECT COUNT(*) FROM opciones o
                      JOIN preguntas p ON p.id_pregunta = o.id_pregunta
                     WHERE p.id_area = %s)                               AS opciones,
                   (SELECT COUNT(*) FROM resultados WHERE id_area = %s)   AS practicas,
                   (SELECT COUNT(DISTINCT id_usuario)
                      FROM resultados WHERE id_area = %s)                 AS estudiantes
            """,
            (id_area, id_area, id_area, id_area),
        )
        resumen = cursor.fetchone()

        # Respuestas dadas a las preguntas de este área.
        cursor.execute(
            """
            SELECT COUNT(*) AS respondidas,
                   COALESCE(SUM(ru.es_correcta), 0) AS acertadas
            FROM respuestas_usuario ru
            JOIN preguntas p ON p.id_pregunta = ru.id_pregunta
            WHERE p.id_area = %s
            """,
            (id_area,),
        )
        respuestas_area = cursor.fetchone()

        # Banco completo (misma consulta que usa el resto del panel).
        cursor.execute(SQL_BANCO, (id_area,))
        preguntas = armar_banco(cursor.fetchall())

        # Actividad de cada pregunta por separado.
        cursor.execute(
            """
            SELECT ru.id_pregunta,
                   COUNT(*) AS respondidas,
                   COALESCE(SUM(ru.es_correcta), 0) AS acertadas,
                   COUNT(DISTINCT ru.id_usuario) AS estudiantes
            FROM respuestas_usuario ru
            JOIN preguntas p ON p.id_pregunta = ru.id_pregunta
            WHERE p.id_area = %s
            GROUP BY ru.id_pregunta
            """,
            (id_area,),
        )
        por_pregunta = {fila["id_pregunta"]: fila for fila in cursor.fetchall()}

        # Cuántos estudiantes eligieron cada opción (letra) de cada pregunta.
        cursor.execute(
            """
            SELECT ru.id_pregunta, o.letra, COUNT(*) AS elegidas
            FROM respuestas_usuario ru
            JOIN preguntas p ON p.id_pregunta = ru.id_pregunta
            JOIN opciones o ON o.id_opcion = ru.id_opcion
            WHERE p.id_area = %s
            GROUP BY ru.id_pregunta, o.letra
            """,
            (id_area,),
        )
        elegidas = {}
        for fila in cursor.fetchall():
            elegidas.setdefault(fila["id_pregunta"], {})[fila["letra"]] = int(
                fila["elegidas"]
            )

    # COUNT() devuelve int y SUM() Decimal: se normalizan a int.
    respondidas = int(respuestas_area["respondidas"])
    acertadas = int(respuestas_area["acertadas"] or 0)
    for clave in ("preguntas", "opciones", "practicas", "estudiantes"):
        resumen[clave] = int(resumen[clave])
    resumen["respondidas"] = respondidas
    resumen["acertadas"] = acertadas
    resumen["precision"] = (
        round(acertadas * 100.0 / respondidas) if respondidas else None
    )

    for pregunta in preguntas:
        cuenta = por_pregunta.get(pregunta["id_pregunta"])
        totales = int(cuenta["respondidas"]) if cuenta else 0
        aciertos = int(cuenta["acertadas"] or 0) if cuenta else 0
        pregunta["respuestas"] = {
            "respondidas": totales,
            "acertadas": aciertos,
            "estudiantes": int(cuenta["estudiantes"]) if cuenta else 0,
            "precision": round(aciertos * 100.0 / totales) if totales else None,
        }
        pregunta["elegidas"] = elegidas.get(pregunta["id_pregunta"], {})

    return jsonify(ok=True, area=area, resumen=resumen, preguntas=preguntas)

# ------------------------------------------------------------------
# Administración (solo usuarios con rol admin)
# ------------------------------------------------------------------
@bp.get("/admin/preguntas")
def admin_preguntas():
    """Banco completo de un area: incluye la respuesta correcta, que el
    administrador necesita para editar."""
    usuario, error = requiere_admin()
    if error:
        return error

    id_area = entero(request.args.get("area"))
    if not id_area:
        return jsonify(ok=False, error="Falta el parametro area."), 400

    filas = consultar(SQL_BANCO, (id_area,))

    return jsonify(ok=True, id_area=id_area, preguntas=armar_banco(filas))


@bp.post("/admin/preguntas")
def admin_crear_pregunta():
    """Crea una pregunta con sus opciones. El numero se asigna solo:
    la pregunta nueva queda al final del area."""
    usuario, error = requiere_admin()
    if error:
        return error

    data = datos()
    id_area = entero(data.get("id_area"))
    if not id_area:
        return jsonify(ok=False, error="Falta el area de la pregunta."), 400

    error_campos, campos = leer_pregunta(data)
    if error_campos:
        return jsonify(ok=False, error=error_campos), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(numero_pregunta), 0) + 1 AS siguiente"
                " FROM preguntas WHERE id_area = %s",
                (id_area,),
            )
            numero = cursor.fetchone()["siguiente"]

            cursor.execute(
                """
                INSERT INTO preguntas
                    (id_area, numero_pregunta, modulo, tema, enunciado, retroalimentacion)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (id_area, numero, campos["modulo"], campos["tema"],
                 campos["enunciado"], campos["retroalimentacion"]),
            )
            id_pregunta = cursor.lastrowid
            guardar_opciones(cursor, id_pregunta, campos["opciones"])
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error al crear la pregunta")
        return jsonify(ok=False, error="No se pudo crear la pregunta."), 500

    return (
        jsonify(ok=True, mensaje="Pregunta creada.",
                id_pregunta=id_pregunta, numero=numero),
        201,
    )


@bp.put("/admin/preguntas/<int:id_pregunta>")
def admin_editar_pregunta(id_pregunta):
    """Edita el enunciado, el tema y las opciones de una pregunta."""
    usuario, error = requiere_admin()
    if error:
        return error

    error_campos, campos = leer_pregunta(datos())
    if error_campos:
        return jsonify(ok=False, error=error_campos), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id_pregunta FROM preguntas WHERE id_pregunta = %s",
                (id_pregunta,),
            )
            if not cursor.fetchone():
                return jsonify(ok=False, error="Esa pregunta no existe."), 404

            cursor.execute(
                """
                UPDATE preguntas
                SET modulo = %s, tema = %s, enunciado = %s, retroalimentacion = %s
                WHERE id_pregunta = %s
                """,
                (campos["modulo"], campos["tema"], campos["enunciado"],
                 campos["retroalimentacion"], id_pregunta),
            )
            editar_opciones(cursor, id_pregunta, campos["opciones"])
        db.commit()
    except OpcionesEnUso:
        db.rollback()
        return (
            jsonify(
                ok=False,
                error="No se puede reducir la cantidad de opciones porque las opciones que se quitarían ya tienen respuestas guardadas.",
            ),
            409,
        )
    except Exception:
        db.rollback()
        logger.exception("Error al editar la pregunta")
        return jsonify(ok=False, error="No se pudo editar la pregunta."), 500

    return jsonify(ok=True, mensaje="Pregunta editada.")


@bp.delete("/admin/preguntas/<int:id_pregunta>")
def admin_borrar_pregunta(id_pregunta):
    """Borra una pregunta. La base borra en cascada sus opciones y las
    respuestas de los usuarios que las referenciaban."""
    usuario, error = requiere_admin()
    if error:
        return error

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM preguntas WHERE id_pregunta = %s", (id_pregunta,)
            )
            borradas = cursor.rowcount
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error al borrar la pregunta")
        return jsonify(ok=False, error="No se pudo borrar la pregunta."), 500

    if not borradas:
        return jsonify(ok=False, error="Esa pregunta no existe."), 404
    return jsonify(ok=True, mensaje="Pregunta borrada junto con sus respuestas.")


@bp.get("/admin/usuarios")
def admin_usuarios():
    """Cuentas registradas con su actividad (prácticas, precisión y última
    práctica). La contraseña nunca sale del servidor."""
    usuario, error = requiere_admin()
    if error:
        return error

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT u.id_usuario, u.nombre, u.apellido, u.correo, u.rol,
                   u.fecha_registro,
                   COUNT(DISTINCT r.id_resultado) AS practicas,
                   COALESCE(SUM(r.respuestas_correctas), 0) AS correctas,
                   COALESCE(SUM(r.preguntas_totales), 0) AS preguntas,
                   MAX(r.fecha_practica) AS ultima_practica
            FROM usuarios u
            LEFT JOIN resultados r ON r.id_usuario = u.id_usuario
            GROUP BY u.id_usuario, u.nombre, u.apellido, u.correo, u.rol,
                     u.fecha_registro
            ORDER BY u.fecha_registro DESC, u.id_usuario DESC
            """
        )
        filas = cursor.fetchall()

    usuarios = []
    for fila in filas:
        preguntas_totales = int(fila["preguntas"] or 0)
        correctas = int(fila["correctas"] or 0)
        usuarios.append(
            {
                "id_usuario": fila["id_usuario"],
                "nombre": fila["nombre"],
                "apellido": fila["apellido"],
                "correo": fila["correo"],
                "rol": fila["rol"],
                # str() deja la fecha como "YYYY-MM-DD HH:MM", que es el
                # formato que leen las páginas del panel.
                "fecha_registro": str(fila["fecha_registro"])
                if fila["fecha_registro"] else None,
                "practicas": int(fila["practicas"]),
                "preguntas_respondidas": preguntas_totales,
                "respuestas_acertadas": correctas,
                "precision": round(correctas * 100.0 / preguntas_totales)
                if preguntas_totales else None,
                "ultima_practica": str(fila["ultima_practica"])
                if fila["ultima_practica"] else None,
            }
        )

    return jsonify(ok=True, usuarios=usuarios)


