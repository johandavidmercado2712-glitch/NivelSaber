"""
Objetivos del estudiante (sólo rol estudiante):

    GET    /api/objetivos      -> objetivos propios con su avance real
    POST   /api/objetivos      -> crea uno (tipo + meta)
    DELETE /api/objetivos/<id> -> borra uno propio

El avance no se guarda en la base: se calcula en cada petición con las
respuestas y prácticas reales de la cuenta (ver avance_usuario en ayudas.py).
"""

import logging

from flask import Blueprint, jsonify

from ayudas import (TIPOS_OBJETIVO, avance_usuario, datos, entero,
                    requiere_estudiante, texto)
from db import get_db

logger = logging.getLogger(__name__)

bp = Blueprint("objetivos", __name__, url_prefix="/api")


# ------------------------------------------------------------------
# Objetivos del estudiante
# ------------------------------------------------------------------

@bp.get("/objetivos")
def listar_objetivos():
    """Objetivos del estudiante con su avance real y el resumen de la cuenta."""
    usuario, error = requiere_estudiante()
    if error:
        return error

    db = get_db()
    with db.cursor() as cursor:
        avance = avance_usuario(cursor, usuario["id"])
        cursor.execute(
            """
            SELECT id_objetivo, tipo, meta
            FROM objetivos
            WHERE id_usuario = %s
            ORDER BY id_objetivo
            """,
            (usuario["id"],),
        )
        filas = cursor.fetchall()

    objetivos = []
    for fila in filas:
        tipo = fila["tipo"]
        meta = int(fila["meta"])
        progreso = int(avance.get(tipo, 0))
        porcentaje = min(round(progreso * 100.0 / meta) if meta else 0, 100)
        objetivos.append(
            {
                "id_objetivo": fila["id_objetivo"],
                "tipo": tipo,
                "meta": meta,
                "titulo": TIPOS_OBJETIVO.get(tipo, tipo).format(meta=meta),
                "progreso": progreso,
                "porcentaje": porcentaje,
                "completado": progreso >= meta,
            }
        )

    return jsonify(ok=True, objetivos=objetivos, avance=avance)


@bp.post("/objetivos")
def crear_objetivo():
    """Crea un objetivo propio (tipo + meta)."""
    usuario, error = requiere_estudiante()
    if error:
        return error

    data = datos()
    tipo = texto(data, "tipo").lower()
    if tipo not in TIPOS_OBJETIVO:
        return jsonify(ok=False, error="Elige un tipo de objetivo válido."), 400

    meta = entero(data.get("meta"))
    if not meta:
        return jsonify(ok=False, error="Escribe una meta mayor que cero."), 400
    if meta > 100000:
        return jsonify(ok=False, error="Esa meta es demasiado grande."), 400
    if tipo == "precision" and meta > 100:
        return jsonify(ok=False, error="La precisión no puede superar el 100%."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS total FROM objetivos WHERE id_usuario = %s",
                (usuario["id"],),
            )
            if int(cursor.fetchone()["total"]) >= 20:
                return (
                    jsonify(
                        ok=False,
                        error="Ya tienes 20 objetivos. Borra alguno antes de crear otro.",
                    ),
                    409,
                )
            cursor.execute(
                "INSERT INTO objetivos (id_usuario, tipo, meta) VALUES (%s, %s, %s)",
                (usuario["id"], tipo, meta),
            )
            id_objetivo = cursor.lastrowid
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error al crear el objetivo")
        return jsonify(ok=False, error="No se pudo crear el objetivo."), 500

    return jsonify(ok=True, mensaje="Objetivo creado.", id_objetivo=id_objetivo), 201


@bp.delete("/objetivos/<int:id_objetivo>")
def borrar_objetivo(id_objetivo):
    """Borra un objetivo propio (el de otra cuenta no se toca)."""
    usuario, error = requiere_estudiante()
    if error:
        return error

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM objetivos WHERE id_objetivo = %s AND id_usuario = %s",
                (id_objetivo, usuario["id"]),
            )
            borrados = cursor.rowcount
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error al borrar el objetivo")
        return jsonify(ok=False, error="No se pudo borrar el objetivo."), 500

    if not borrados:
        return jsonify(ok=False, error="Ese objetivo no existe."), 404
    return jsonify(ok=True, mensaje="Objetivo eliminado.")


