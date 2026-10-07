/*
 * Muestra en el encabezado al usuario que realmente tiene la sesión abierta.
 *
 * - Rellena el avatar y el nombre del chip de perfil en todas las páginas.
 * - Si la página declara <body data-requiere-sesion>, sin sesión se redirige
 *   a login.html: el banco de preguntas y los resultados sólo se ven logueado.
 * - Si el <h1> lleva data-saludo, se le añade el nombre.
 */

document.addEventListener("DOMContentLoaded", async function () {
    const datos = await apiGET("sesion");
    const usuario = datos && datos.usuario;

    if (!usuario) {
        document.querySelectorAll(".perfil-nombre").forEach(function (nodo) {
            nodo.textContent = "Invitado";
        });
        document.querySelectorAll(".perfil-avatar").forEach(function (nodo) {
            nodo.textContent = "?";
        });

        if (document.body.hasAttribute("data-requiere-sesion")) {
            location.href = RAIZ + "login.html";
        }
        return;
    }

    const rol = String(usuario.rol || "").trim().toLowerCase();
    const rolRequerido = document.body.dataset.rolRequerido;
    if (rol !== "admin" && rol !== "estudiante") {
        location.href = RAIZ + "login.html";
        return;
    }

    // Sesión guardada sin rol (por ejemplo, una cookie creada por una versión
    // antigua del servidor): sin este guardia la página se redirigiría a sí
    // misma en bucle. Se pide volver a entrar para refrescar la sesión.
    if (rolRequerido && !rol) {
        location.href = RAIZ + "login.html";
        return;
    }

    if (rolRequerido && rol !== rolRequerido) {
        const destino = rol === "admin"
            ? RAIZ + "barralateral/admin.html"
            : RAIZ + "index.html";
        const actual = location.pathname;
        const yaEstaEnDestino = rol === "admin"
            ? actual.endsWith("/barralateral/admin.html")
            : actual.endsWith("/index.html") || actual === "/";
        if (!yaEstaEnDestino) location.replace(destino);
        return;
    }

    const iniciales = (usuario.nombre || "").trim().charAt(0).toUpperCase() || "E";
    const nombre = [usuario.nombre, usuario.apellido].filter(Boolean).join(" ");

    document.querySelectorAll(".perfil-nombre").forEach(function (nodo) {
        nodo.textContent = nombre;
    });
    document.querySelectorAll(".perfil-avatar").forEach(function (nodo) {
        nodo.textContent = iniciales;
    });

    // El enlace de administración solo se muestra a usuarios con rol admin.
    const enlaceAdmin = document.getElementById("enlaceAdmin");
    if (enlaceAdmin) enlaceAdmin.hidden = rol !== "admin";

    const saludo = document.querySelector("h1[data-saludo]");
    if (saludo) {
        saludo.textContent = saludo.textContent.replace("¡Hola!", "¡Hola, " + usuario.nombre + "!");
    }
});
