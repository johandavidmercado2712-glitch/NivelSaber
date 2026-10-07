# Backend de NIVELSABER

El backend es una API REST escrita en Python con Flask. Atiende las
peticiones bajo `/api/`, valida las sesiones y los roles, y lee o modifica
la base de datos MariaDB/MySQL mediante PyMySQL.

## Requisitos

- Python compatible con Flask 3.1.
- MariaDB/MySQL activo (la configuración actual está preparada para XAMPP).
- Una base llamada `nivelesaber` con las tablas principales del proyecto.
- Apache y sus módulos de proxy y reescritura si se va a usar el frontend
  desde la misma instalación de XAMPP.

## Base de datos en phpMyAdmin

La conexión actual está definida en [`backend/db.py`](backend/db.py):

| Ajuste | Valor actual |
| --- | --- |
| Host | `127.0.0.1` |
| Puerto | `3306` |
| Base | `nivelesaber` |
| Usuario | `root` |
| Contraseña | Vacía |

Si tu instalación usa otros datos, actualiza esos valores antes de arrancar
Flask.

En phpMyAdmin, selecciona `nivelesaber` y usa **Importar** para cargar los
scripts necesarios:

1. `backend/admin.sql`: agrega el rol de usuario si falta y marca
   `estudiante@gmail.com` como administrador. Para usar otra cuenta, cambia
   el `UPDATE` de ese script por el correo que ya tengas registrado.
2. `backend/semillas.sql`: aplica cambios al esquema y carga áreas y
   preguntas de demostración.
3. `backend/objetivos.sql`: crea la tabla de objetivos.

Si vas a ampliar una base que ya tiene preguntas, **no vuelvas a importar
`backend/semillas.sql`**: ese script elimina las preguntas antes de cargar
las de ejemplo. Ejecuta solo el cargador de talleres descrito abajo.

Después de importar los scripts SQL y preparar la conexión, agrega cinco
talleres de diez preguntas por área sin borrar el contenido anterior.
Ejecuta el validador y luego el cargador desde la raíz del proyecto:

   ```bash
   venv/bin/python backend/cargar_talleres.py --validar
   venv/bin/python backend/cargar_talleres.py
   ```

La carga usa la conexión configurada en `backend/db.py`, asigna números
nuevos a las preguntas y se puede repetir sin duplicarlas. También valida
que cada pregunta existente tenga sus cuatro opciones y una respuesta
correcta. El banco anterior se conserva y aparece como una práctica
independiente llamada **Preguntas anteriores**.

**Importante:** estos scripts esperan que ya existan las tablas principales
(`usuarios`, `areas`, `preguntas`, `opciones`, `resultados` y
`respuestas_usuario`). Este repositorio no incluye un script que cree desde
cero todo ese esquema. Además, `semillas.sql` elimina las preguntas
existentes antes de volver a cargar las de demostración; no lo importes en
una base con preguntas o respuestas que quieras conservar.

## Instalar e iniciar

Desde la carpeta raíz del proyecto:

```bash
python3 -m venv venv
venv/bin/pip install -r backend/requirements.txt
```

Si ya existe `venv`, no hace falta recrearlo. Inicia la API:

```bash
venv/bin/python backend/app.py
```

El servidor de desarrollo de Flask escucha en `127.0.0.1:5000`. Déjalo
corriendo en esa terminal. Si aparece `Address already in use`, ya hay un
proceso usando el puerto; comprueba primero si la API existente funciona
antes de iniciar otra instancia.

Comprueba API y conexión a la base de datos:

```bash
curl -i http://127.0.0.1:5000/api/salud
```

La respuesta correcta es `200 OK` con un JSON como:

```json
{"ok": true, "mensaje": "conexion a la base de datos correcta"}
```

## Organización

- `backend/app.py`: crea la aplicación Flask e incorpora los blueprints.
- `backend/rutas_cuentas.py`: registro, login, logout y consulta de sesión.
- `backend/rutas_practica.py`: áreas visibles, preguntas, envío de
  respuestas, resultados e historial de estudiantes.
- `backend/rutas_admin.py`: gestión de áreas, preguntas, respuestas y
  consulta de cuentas para administración.
- `backend/rutas_objetivos.py`: lectura y gestión de objetivos de
  estudiantes.
- `backend/ayudas.py`: validaciones, autorización por rol y utilidades
  comunes de preguntas.
- `backend/db.py`: conexión y consultas a MariaDB/MySQL.

El registro crea usuarios con rol `estudiante`. El acceso administrativo
requiere que la cuenta tenga el rol `admin`. El backend aplica esa
restricción en las rutas; ocultar páginas o botones en el navegador no es
el mecanismo de autorización.

## Rutas principales

| Método | Ruta | Uso |
| --- | --- | --- |
| `POST` | `/api/registro` | Crear cuenta de estudiante |
| `POST` | `/api/login` | Iniciar sesión |
| `POST` | `/api/logout` | Cerrar sesión |
| `GET` | `/api/sesion` | Consultar el usuario de la sesión |
| `GET` | `/api/areas` | Listar áreas y cantidad de preguntas |
| `GET` | `/api/talleres?area=<id>` | Listar talleres disponibles en un área |
| `GET` | `/api/preguntas?area=<id>&taller=<nombre>` | Obtener preguntas de un taller |
| `POST` | `/api/respuestas` | Calificar y guardar una práctica |
| `GET` | `/api/resultados`, `/api/historial` | Resultados e historial del estudiante |
| `GET`, `POST`, `PUT`, `DELETE` | `/api/objetivos...` | Objetivos del estudiante |
| `GET`, `POST`, `PUT`, `DELETE` | `/api/admin/areas...` | Consultar y administrar áreas |
| `GET`, `POST`, `PUT`, `DELETE` | `/api/admin/preguntas...` | Administrar preguntas y opciones |
| `GET` | `/api/admin/usuarios` | Consultar cuentas y su actividad |
| `GET` | `/api/salud` | Verificar Flask y base de datos |

Las rutas de administración exigen sesión con rol `admin`. Las rutas de
práctica, resultados e historial son para estudiantes.

## Servir el frontend junto con la API

Flask proporciona la API, no las páginas HTML. El archivo
[`.htaccess`](.htaccess) del proyecto reenvía `/api/...` a Flask en el puerto
5000. Por eso, para usar la aplicación completa, Apache debe servir la
carpeta del proyecto —normalmente como
`/opt/lampp/htdocs/nivelsaber`— y tener habilitados `mod_rewrite`,
`mod_proxy`, `mod_proxy_http` y `mod_headers`.

Con XAMPP instalado en `/opt/lampp`, inicia Apache y MariaDB con:

```bash
sudo /opt/lampp/lampp start
```

Luego abre `http://localhost/nivelsaber/`. No uses VS Code Live Server para
el login: Live Server no aplica `.htaccess`, así que el `POST /api/login`
puede terminar en un `405 Method Not Allowed`.

## Configuración de despliegue

El backend acepta estas variables de conexión, que deben apuntar a una base
remota separada para la demo:

| Variable preferida | Alternativa Railway | Valor local predeterminado |
| --- | --- | --- |
| `DB_HOST` | `MYSQLHOST` | `127.0.0.1` |
| `DB_PORT` | `MYSQLPORT` | `3306` |
| `DB_NAME` | `MYSQLDATABASE` | `nivelesaber` |
| `DB_USER` | `MYSQLUSER` | `root` |
| `DB_PASSWORD` | `MYSQLPASSWORD` | Vacío |

Para alojarla, el repositorio incluye `Procfile`, `render.yaml`,
`railway.json`, `backend/gunicorn.conf.py` y un `requirements.txt` de raíz
que instala Gunicorn junto con las dependencias de Flask.

### Crear una copia de demo en Railway

1. Crea una base MySQL de Railway en el mismo proyecto que el servicio web.
   Conserva la base local de XAMPP sin exponerla a Internet.
2. Desde phpMyAdmin, exporta la base actual a un archivo SQL y revisa su
   contenido antes de importarlo: elimina cuentas reales, correos, nombres,
   resultados u otra información personal que no debas publicar. Conserva
   el esquema, las áreas y las preguntas que quieras demostrar. No importes
   datos reales de estudiantes al servicio público.
3. Importa la copia revisada en la base MySQL de Railway. Los scripts
   `semillas.sql` y `admin.sql` son para cambios/carga de demostración y no
   sustituyen el esquema completo. Evita `semillas.sql` si no quieres que se
   borren las preguntas de esa copia.
4. Conecta el repositorio GitHub al servicio Railway. Configura
   `NIVELSABER_CLAVE_SECRETA` con un secreto aleatorio privado y
   `APP_ENV=production`. Si Railway no comparte automáticamente las
   variables de MySQL, asigna `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y
   `DB_PASSWORD` usando los valores internos del servicio de base de datos.
5. Despliega. El proceso de inicio configurado usa Gunicorn, sirve tanto el
   frontend como la API desde un solo origen y enlaza el puerto `PORT` de la
   plataforma. Comprueba `<URL-del-servicio>/api/salud`.
6. Abre `<URL-del-servicio>/login.html`, registra un estudiante de demo y
   prueba el flujo. Mantén la cuenta administradora fuera del enlace público
   salvo que aceptes que los visitantes administren la copia compartida.

`render.yaml` también permite crear el servicio web en Render, pero Render
no convierte el MySQL local de XAMPP en una base remota; configura igualmente
una base MySQL externa y copia solo los datos sanitizados. Define allí las
variables `DB_*` solicitadas por el blueprint.

La clave de sesión predeterminada solo sirve para desarrollo local. En
producción la aplicación requiere `NIVELSABER_CLAVE_SECRETA` y marca la
cookie de sesión como segura (`Secure`). No publiques el servidor de
desarrollo de Flask ni uses la cuenta MySQL `root` sin contraseña en un
servidor expuesto.

## Solución de problemas

- **`Address already in use` en el puerto 5000:** la API puede estar ya
  activa; prueba `/api/salud` antes de hacer nada.
- **`405` al iniciar sesión:** abre el sitio mediante Apache en
  `http://localhost/nivelsaber/`, no mediante Live Server.
- **`500` en `/api/salud`:** revisa que MariaDB esté activo, que exista la
  base y que las credenciales en `backend/db.py` coincidan.
- **`403` en una ruta de administración:** comprueba en phpMyAdmin que el
  usuario de la sesión tenga `rol = 'admin'`; cierra la sesión y vuelve a
  entrar tras cambiar el rol.
- **No se encuentra una tabla:** las migraciones de este repositorio no
  crean el esquema principal desde cero; importa primero el esquema base de
  la instalación del proyecto.
