/* ------------------------------------------------------------------
 * NIVELSABER - utilidades de JavaScript
 *
 * funciones pequeñas y reutilizables que usan varias páginas.
 * - esc(valor): convierte un texto en safe HTML (evita que un
 *               dato del servidor rompa la página o pueda inyectar código).
 *               Úsalo siempre que pases datos del servidor a HTML.
 *
 * Uso: <script src="js/util.js"></script> antes del script que la usa.
 * ------------------------------------------------------------------ */

function esc(valor) {
    // Convierte null/undefined a cadena vacía, luego escapa los
    // caracteres HTML especiales: < > & " '
    return String(valor === null || valor === undefined ? "" : valor)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}
