# Frontend de NIVELSABER

El frontend es una aplicación web estática hecha con HTML, CSS y JavaScript
sin proceso de compilación ni administrador de paquetes. Presenta las
pantallas de autenticación, áreas de práctica, resultados, objetivos, perfil
y administración. Los datos se obtienen de la API Flask; el navegador no
consulta la base de datos directamente.

## Requisitos

- Backend Flask en ejecución en `127.0.0.1:5000`.
- Base de datos activa y preparada; consulta
  [`README_BACKEND.md`](README_BACKEND.md).
- Apache sirviendo esta carpeta con reglas `.htaccess` habilitadas.

## Cómo ejecutarlo en XAMPP

1. Inicia Apache y MariaDB desde el panel de XAMPP o, en Linux:

   ```bash
   sudo /opt/lampp/lampp start
   ```

2. Asegúrate de que el proyecto esté publicado bajo
   `/opt/lampp/htdocs/nivelsaber`. Si lo copiaste allí con otro nombre,
   usa esa ruta en los pasos siguientes.
3. En la raíz del proyecto, instala dependencias e inicia el backend en una
   terminal:

   ```bash
   venv/bin/pip install -r backend/requirements.txt
   venv/bin/python backend/app.py
   ```

   Mantén esa terminal abierta mientras uses la web.
4. Abre `http://localhost/nivelsaber/` o
   `http://localhost/nivelsaber/login.html`.

La regla de [`.htaccess`](.htaccess) reenvía las peticiones `/api/` de
Apache a Flask. No abras el login desde VS Code Live Server: no ejecuta
`.htaccess` y las peticiones POST a la API pueden devolver `405`.

## Publicar una demo en la nube

El backend también puede servir el frontend bajo el mismo dominio. Los
archivos `Procfile`, `render.yaml`, `railway.json` y el `requirements.txt`
de la raíz permiten desplegarlo con Gunicorn en Railway o Render; no se usa
`.htaccess` en ese despliegue.

Antes de compartir el enlace:

1. Sube el proyecto a un repositorio GitHub y conecta el servicio web de
   Railway o Render.
2. Crea una base MySQL remota y configura las variables que documenta
   [`README_BACKEND.md`](README_BACKEND.md).
3. Exporta la base desde phpMyAdmin, quita datos personales y credenciales
   reales, e importa el esquema y el contenido de demostración a la base
   remota. El servicio publicado no puede conectarse a `127.0.0.1` de tu
   computador.
4. Genera un secreto de sesión para producción y establece
   `APP_ENV=production`.
5. Tras desplegar, prueba la URL `/api/salud`, el registro y una práctica
   antes de compartir `<URL-del-servicio>/login.html`.

La demo es interactiva y escribe en la copia remota: los registros,
resultados y cambios administrativos los verán también otros visitantes.
No compartas la cuenta de administración si no quieres que los visitantes
editen el contenido de demostración.

## Flujo de uso

1. `crearCuenta.html` envía nombre, apellido, correo y contraseña a
   `POST /api/registro`. El servidor valida los campos y guarda la
   contraseña como hash. Las cuentas creadas reciben el rol `estudiante`.
2. `login.html` envía las credenciales a `POST /api/login`. Flask guarda la
   sesión en una cookie del mismo sitio y devuelve el rol. El frontend
   dirige estudiantes a `index.html` y administradores al dashboard
   `barralateral/admin.html`.
3. El JavaScript de cada pantalla utiliza `js/api.js` para llamar a la
   API. Si una ruta necesita autenticación y la sesión no existe, la API
   responde `401` y el cliente vuelve al login.
4. En la sección de práctica, el estudiante elige un área y luego un taller.
   El frontend recibe solo las preguntas y opciones de ese taller, sin
   conocer las respuestas correctas. Al enviar, el backend valida que todas
   las respuestas pertenezcan al taller, califica la prueba y registra el
   resultado con el nombre del taller para mostrarlo en resultados e
   historial. Cada respuesta correcta suma un punto.
5. El panel admin permite administrar áreas y preguntas con sus opciones,
   consultar el detalle/actividad de un área y revisar las cuentas
   registradas. La API valida el rol `admin` para esas operaciones.

## Archivos relevantes

- `login.html`, `crearCuenta.html`: autenticación.
- `index.html`: inicio del estudiante y marca NIVELSABER.
- `img/logo.png`: logo compartido por el login y la página de inicio.
- `barralateral/areas.html`, `barralateral/praticar.html`: selección de
  áreas, talleres y práctica.
- `barralateral/perfil.html`, `barralateral/misobjetivos.html`: perfil y
  objetivos.
- `barralateral/admin.html`: dashboard administrativo.
- `js/api.js`: cliente común para llamadas a la API y rutas relativas.
- `js/registro.js`: registro, login y control para mostrar la contraseña.
- `js/sesion.js`: muestra el usuario y aplica redirecciones de páginas
  según sesión y rol.
- `js/script.js`, `js/resultados.js`, `js/objetivos.js`, `js/perfil.js`,
  `js/admin.js`: comportamiento de las distintas secciones.
- `css/`: estilos generales, de acceso, de páginas y de administración.

## Roles y navegación

- **Estudiante:** ve las páginas de práctica, perfil, resultados e
  historial; cada pantalla muestra los datos de la cuenta autenticada.
- **Administrador:** se dirige al dashboard y gestiona el contenido desde
  sus secciones de áreas/preguntas, detalle y estudiantes.

Las comprobaciones del frontend mejoran la navegación y la experiencia,
pero no sustituyen la autorización del backend. No conviertas una cuenta en
administradora cambiando JavaScript; asígnale el rol en phpMyAdmin y vuelve
a iniciar sesión para renovar la cookie.

## Comprobaciones rápidas

Comprueba que el logo se descarga desde
`http://localhost/nivelsaber/img/logo.png` (debe responder `200`).

API y conexión con la base:

```text
http://localhost/nivelsaber/api/salud
```

Debe responder un JSON con `"ok": true`. También puedes usar:

```bash
curl -i http://localhost/nivelsaber/api/salud
```

Si Apache devuelve `404` en CSS o JavaScript, comprueba que el sitio esté
abierto bajo la ruta correcta (`/nivelsaber/`) y que la carpeta publicada
contenga los archivos `css/`, `js/` y `barralateral/`.

Si acabas de actualizar archivos y ves la versión anterior, fuerza la
recarga del navegador (`Ctrl+Shift+R`).
