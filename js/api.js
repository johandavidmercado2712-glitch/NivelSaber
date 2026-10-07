/*
 * Acceso a la API de NIVELSABER.
 *
 * La misma carpeta de JavaScript sirve a páginas de la raíz (index.html,
 * login.html) y a páginas dentro de barralateral/. La API sólo está
 * publicada bajo /api/ de la raíz, así que se calcula una ruta relativa.
 */

const RAIZ = location.pathname.indexOf("/barralateral/") >= 0 ? "../" : "";
const API_BASE = RAIZ + "api/";

function apiGET(ruta) {
    return apiFetch(ruta, { method: "GET" });
}

function apiPOST(ruta, cuerpo) {
    return apiFetch(ruta, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cuerpo),
    });
}

function apiPUT(ruta, cuerpo) {
    return apiFetch(ruta, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cuerpo),
    });
}

function apiDEL(ruta) {
    return apiFetch(ruta, { method: "DELETE" });
}

async function apiFetch(ruta, opciones) {
    let respuesta;
    try {
        respuesta = await fetch(API_BASE + ruta, opciones);
    } catch (error) {
        return { ok: false, error: "No se pudo conectar con el servidor. ¿Está corriendo?" };
    }

    if (respuesta.status === 401) {
        // Sin sesión no hay práctica posible: se vuelve al inicio de sesión.
        location.href = RAIZ + "login.html";
        return { ok: false, error: "Debes iniciar sesión.", redirigiendo: true };
    }

    try {
        return await respuesta.json();
    } catch (error) {
        return { ok: false, error: "El servidor devolvió una respuesta inesperada." };
    }
}
