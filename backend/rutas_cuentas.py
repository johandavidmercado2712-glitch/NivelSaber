"""
Cuentas de usuario: registro, login, logout y sesión.

    POST /api/registro  -> crea una cuenta
    POST /api/login     -> inicia sesión (guarda al usuario en la cookie)
    POST /api/logout    -> cierra sesión
    GET  /api/sesion    -> devuelve el usuario de la sesión actual

El prefijo /api lo indica el Blueprint en app.py.
"""

import logging

import pymysql
from flask import Blueprint, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from ayudas import datos, texto
from db import get_db

logger = logging.getLogger(__name__)

bp = Blueprint("cuentas", __name__, url_prefix="/api")


# ------------------------------------------------------------------
# Cuentas
# ------------------------------------------------------------------
@bp.post("/registro")
def registro():
    data = datos()
    nombre = texto(data, "nombre")
    apellido = texto(data, "apellido")
    correo = texto(data, "correo", "email").lower()
    clave = texto(data, "contrasena", "password")
    confirmar = texto(data, "confirmar", "confirm_password", "confirm-password")

    if not nombre:
        return jsonify(ok=False, error="Escribe tu nombre."), 400
    if not apellido:
        return jsonify(ok=False, error="Escribe tu apellido."), 400
    if "@" not in correo or "." not in correo:
        return jsonify(ok=False, error="Escribe un correo valido."), 400
    if len(clave) < 6:
        return jsonify(ok=False, error="La contrasena debe tener al menos 6 caracteres."), 400
    if clave != confirmar:
        return jsonify(ok=False, error="Las contrasenas no coinciden."), 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO usuarios (nombre, apellido, correo, rol, contrasena)"
                " VALUES (%s, %s, %s, 'estudiante', %s)",
                (
                    nombre,
                    apellido,
                    correo,
                    generate_password_hash(clave, method="pbkdf2:sha256"),
                ),
            )
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        return jsonify(ok=False, error="Este correo ya tiene una cuenta. Inicia sesion."), 409
    except Exception:
        db.rollback()
        logger.exception("Error al registrar")
        return jsonify(ok=False, error="No se pudo crear la cuenta."), 500

    return jsonify(ok=True, mensaje="Cuenta creada."), 201


@bp.post("/login")
def login():
    data = datos()
    correo = texto(data, "correo", "email").lower()
    clave = texto(data, "contrasena", "password")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT id_usuario, nombre, apellido, correo, rol, contrasena"
            " FROM usuarios WHERE correo = %s",
            (correo,),
        )
        usuario = cursor.fetchone()

    # Mismo mensaje sea cual sea el motivo: no se revela si falto el correo o la clave.
    if not usuario or not check_password_hash(usuario["contrasena"], clave):
        return jsonify(ok=False, error="Correo o contrasena incorrectos. Intenta de nuevo."), 401

    session.clear()
    session["usuario"] = {
        "id": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "apellido": usuario["apellido"],
        "correo": usuario["correo"],
        "rol": usuario["rol"],
    }
    return jsonify(ok=True, usuario=session["usuario"])


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify(ok=True, mensaje="Sesion cerrada.")


@bp.get("/sesion")
def sesion():
    return jsonify(ok=True, usuario=session.get("usuario"))


