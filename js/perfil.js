/*
 * NIVELSABER - Ficha de perfil.
 *
 * Rellena la tarjeta con el usuario de la sesión y los KPIs con
 * GET /api/estadisticas (precisión, prácticas y áreas del historial).
 */

document.addEventListener("DOMContentLoaded", async function () {
    const salir = document.getElementById("btnSalir");
    if (salir) {
        salir.addEventListener("click", async function () {
            salir.disabled = true;
            await apiPOST("logout", {});
            location.href = RAIZ + "login.html";
        });
    }

    const [sesion, resumen] = await Promise.all([apiGET("sesion"), apiGET("estadisticas")]);
    if (!sesion.ok) return; // Sin sesión api.js ya redirigió.

    if (sesion.usuario) {
        const u = sesion.usuario;
        const nombre = [u.nombre, u.apellido].filter(Boolean).join(" ");
        document.getElementById("perfilNombre").textContent = nombre;
        document.getElementById("perfilCorreo").textContent = u.correo || "—";
        document.getElementById("perfilAvatar").textContent =
            (u.nombre || "").trim().charAt(0).toUpperCase() || "E";
    }

    if (!resumen.ok) return;
    const e = resumen.estadisticas;

    document.getElementById("kpiPrecision").textContent =
        e.precision === null ? "—" : e.precision + "%";
    document.getElementById("kpiPracticas").textContent = e.practicas;
    document.getElementById("kpiAreas").textContent = e.areas_completadas + "/5";
});
