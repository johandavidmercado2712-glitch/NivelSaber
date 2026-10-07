"""
Conexion a la base de datos 'nivelesaber' (MariaDB/MySQL).

En local usa los valores predeterminados de XAMPP. En despliegues lee las
variables DB_* o las variables MYSQL* que Railway asigna al servicio MySQL.
"""

import os

import pymysql
from flask import g
from pymysql.cursors import DictCursor


def variable(nombre, alternativo, predeterminado):
    """Lee una variable DB_* y acepta como alternativa la convención MYSQL*."""
    valor = os.environ.get(nombre)
    if valor is not None:
        return valor
    valor = os.environ.get(alternativo)
    if valor is not None:
        return valor
    return predeterminado


def conectar():
    """Devuelve una conexion nueva a la base de datos."""
    return pymysql.connect(
        host=variable("DB_HOST", "MYSQLHOST", "127.0.0.1"),
        port=int(variable("DB_PORT", "MYSQLPORT", "3306")),
        user=variable("DB_USER", "MYSQLUSER", "root"),
        password=variable("DB_PASSWORD", "MYSQLPASSWORD", ""),
        database=variable("DB_NAME", "MYSQLDATABASE", "nivelesaber"),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


def get_db():
    """Devuelve la conexion de la peticion actual (se reutiliza si ya existe)."""
    if "db" not in g:
        g.db = conectar()
    return g.db


def close_db(error=None):
    """Cierra la conexion al terminar la peticion."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def consultar(sql, params=()):
    """Ejecuta una consulta de LECTURA y devuelve las filas (lista de dicts).

    Es el atajo para las rutas que sólo leen datos y no necesitan
    transacciones. En vez de escribir siempre:

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(sql, params)
            filas = cursor.fetchall()

    basta con:

        filas = consultar(sql, params)
    """
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()
