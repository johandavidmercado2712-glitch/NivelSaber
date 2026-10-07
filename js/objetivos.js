/*
 * NIVELSABER - Mis objetivos.
 *
 * Habla con estas rutas del servidor:
 *   GET    /api/objetivos     -> objetivos propios con su avance real
 *   POST   /api/objetivos     -> crea uno (tipo + meta)
 *   DELETE /api/objetivos/N   -> borra uno propio
 *
 * Aquí no se guarda nada en el navegador: los objetivos viven en la
 * base de datos, así cada cuenta ve sólo los suyos y una cuenta nueva
 * empieza sin objetivos (estado vacío).
 */

let objetivosActuales = [];

/* Igual que en script.js: evita que el texto del banco rompa el HTML. */


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("formObjetivo").addEventListener("submit", crearObjetivo);
    cargarObjetivos();
});

async function cargarObjetivos() {
    const lista = document.getElementById("listaObjetivos");
    const datos = await apiGET("objetivos");
    if (!datos.ok) {
        // Sin sesión api.js ya redirigió; aquí sólo queda el error.
        lista.innerHTML = '<p class="objetivo-vacio">' + esc(datos.error) + "</p>";
        return;
    }

    objetivosActuales = datos.objetivos;
    pintarResumen(datos);
    pintarLista();
}

function pintarResumen(datos) {
    const completados = datos.objetivos.filter(function (objetivo) {
        return objetivo.completado;
    }).length;

    document.getElementById("kpiActivos").textContent = datos.objetivos.length;
    document.getElementById("kpiCompletados").textContent = completados;
    document.getElementById("kpiPrecision").textContent =
        (datos.avance ? datos.avance.precision : null) + "%";
}

function pintarLista() {
    const lista = document.getElementById("listaObjetivos");

    if (!objetivosActuales.length) {
        lista.innerHTML =
            '<p class="objetivo-vacio">Aún no has creado objetivos. ' +
            "Usa el formulario para definir tu primera meta: " +
            "el avance se calcula solo con tus respuestas y prácticas reales.</p>";
        return;
    }

    lista.innerHTML = objetivosActuales.map(function (objetivo) {
        return (
            '<div class="barra-item">' +
            "<span>" + esc(objetivo.titulo) + " <b>" + objetivo.porcentaje + "%</b></span>" +
            '<div class="barra-pista"><div class="barra-lleno" style="width:' +
            objetivo.porcentaje + '%;"></div></div>' +
            '<small class="objetivo-meta">' + objetivo.progreso + "/" + objetivo.meta +
            (objetivo.completado ? " ✓ completado" : "") + "</small>" +
            '<button type="button" class="objetivo-borrar" data-borrar="' +
            objetivo.id_objetivo + '" title="Borrar objetivo" ' +
            'aria-label="Borrar objetivo">✕</button>' +
            "</div>"
        );
    }).join("");

    lista.querySelectorAll("[data-borrar]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            borrarObjetivo(Number(boton.dataset.borrar));
        });
    });
}

async function crearObjetivo(evento) {
    evento.preventDefault();
    const caja = document.getElementById("mensajeObjetivo");

    const datos = await apiPOST("objetivos", {
        tipo: document.getElementById("tipoObjetivo").value,
        meta: Number(document.getElementById("metaObjetivo").value),
    });

    if (!datos.ok) {
        mostrarMensaje(caja, datos.error, "error");
        return;
    }

    mostrarMensaje(caja, datos.mensaje, "exito");
    document.getElementById("metaObjetivo").value = "";
    await cargarObjetivos();
    setTimeout(function () { mostrarMensaje(caja, "", ""); }, 2500);
}

async function borrarObjetivo(idObjetivo) {
    if (!confirm("¿Borrar este objetivo?")) return;

    const datos = await apiDEL("objetivos/" + idObjetivo);
    if (!datos.ok) {
        alert(datos.error);
        return;
    }

    await cargarObjetivos();
}

function mostrarMensaje(caja, texto, tipo) {
    caja.textContent = texto;
    caja.className = texto ? "mensaje " + tipo : "mensaje";
}