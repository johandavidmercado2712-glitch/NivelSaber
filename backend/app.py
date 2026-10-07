"""
NIVELSABER - API en Flask (punto de entrada)

Este archivo SÓLO arma la aplicación: crea Flask, activa la sesión y
conecta los módulos de rutas. Cada grupo de rutas vive en su archivo:

    rutas_cuentas.py     registro, login, logout y sesión
    rutas_practica.py    áreas, preguntas, respuestas, resultados e historial
    rutas_admin.py       administración (rol admin)
    rutas_objetivos.py   objetivos del estudiante
    ayudas.py            funciones compartidas (validaciones, roles, banco)
    db.py                conexión a la base de datos 'nivelesaber'

Todas las rutas empiezan con /api/ (el prefijo lo pone cada Blueprint).
Las de práctica exigen sesión; las de administración exigen rol admin.

Para arrancar:   venv/bin/python app.py
Después abrir:   http://localhost/nivelsaber/
"""

import os
from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory

from db import close_db, get_db
from rutas_admin import bp as bp_admin
from rutas_cuentas import bp as bp_cuentas
from rutas_objetivos import bp as bp_objetivos
from rutas_practica import bp as bp_practica

app = Flask(__name__)

ES_PRODUCCION = os.environ.get("APP_ENV", "").lower() == "production"
CLAVE_SECRETA = os.environ.get("NIVELSABER_CLAVE_SECRETA")
if ES_PRODUCCION and not CLAVE_SECRETA:
    raise RuntimeError("Configura NIVELSABER_CLAVE_SECRETA en el entorno de despliegue.")

app.secret_key = CLAVE_SECRETA or "clave-local-solo-para-desarrollo"
# La cookie de sesión sólo viaja entre páginas de este mismo sitio.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = ES_PRODUCCION

# Cierra la base de datos al terminar cada petición.
app.teardown_appcontext(close_db)

# Conexión de cada módulo de rutas (todas quedan bajo /api/...).
app.register_blueprint(bp_cuentas)
app.register_blueprint(bp_practica)
app.register_blueprint(bp_admin)
app.register_blueprint(bp_objetivos)

CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
PAGINAS_PUBLICAS = {"index.html", "login.html", "crearCuenta.html"}


@app.get("/")
def inicio():
    return send_from_directory(CARPETA_PROYECTO, "index.html", max_age=0)


@app.get("/<path:archivo>")
def archivo_raiz(archivo):
    if archivo not in PAGINAS_PUBLICAS:
        abort(404)
    return send_from_directory(CARPETA_PROYECTO, archivo, max_age=0)


@app.get("/css/<path:archivo>")
def archivo_css(archivo):
    return send_from_directory(CARPETA_PROYECTO / "css", archivo, max_age=0)


@app.get("/js/<path:archivo>")
def archivo_javascript(archivo):
    return send_from_directory(CARPETA_PROYECTO / "js", archivo, max_age=0)


@app.get("/img/<path:archivo>")
def archivo_imagen(archivo):
    return send_from_directory(CARPETA_PROYECTO / "img", archivo, max_age=0)


@app.get("/barralateral/<path:archivo>")
def pagina_aplicacion(archivo):
    return send_from_directory(CARPETA_PROYECTO / "barralateral", archivo, max_age=0)


@app.get("/api/salud")
def salud():
    """Comprueba que Flask y la base de datos responden."""
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        app.logger.exception("Fallo la conexion a la base de datos")
        return jsonify(ok=False, error="No se pudo conectar a la base de datos."), 500
    return jsonify(ok=True, mensaje="conexion a la base de datos correcta")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
    )
