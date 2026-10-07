/*
 * NIVELSABER - Resultados de práctica.
 *
 * Pinta las tres pestañas de praticar.html:
 *
 *   📈 Última     GET /api/resultados -> KPIs, dona, áreas y errores de la
 *                                       última prueba.
 *   🗓️ Historial  GET /api/historial  -> lista paginada de todas las prácticas,
 *                                       con detalle que se carga al abrir cada
 *                                       fila y chips de filtro por área.
 *   🎯 Por tema   GET /api/historial  -> campo "temas": precisión agregada por
 *                                       módulo/tema, de la más débil a la más
 *                                       fuerte.
 */



const CIRCUNFERENCIA_DONA = 439.82; // 2 * PI * 70
const MESES = ["ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic"];

const SUBTITULOS = {
    ultima: "Este es el detalle de tu última prueba",
    historial: "Todas tus prácticas, de la más reciente a la más antigua",
    temas: "Dónde te va bien y dónde debes reforzar",
};

// Estado de la pestaña Historial. La primera carga trae a la vez la lista
// de la página 1, los filtros y el desempeño por tema.
let cacheHistorial = null;
let cargandoHistorial = false;
let paginaActual = 1;
let areaActual = "";


// ------------------------------------------------------------------
// Utilidades
// ------------------------------------------------------------------

function escResultado(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, function (caracter) {
        return {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        }[caracter];
    });
}

/**
 * "2026-10-05 19:20:50" -> "5 oct 2026 · 19:20".
 * Se parsea a mano: new Date() con espacio no es fiable en todos los
 * navegadores y aquí sólo hace falta formato de lectura.
 */
function fechaLegible(valor) {
    const partes = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/.exec(String(valor || ""));
    if (!partes) return String(valor || "");
    return (
        Number(partes[3]) + " " + MESES[Number(partes[2]) - 1] + " " + partes[1] +
        " · " + partes[4] + ":" + partes[5]
    );
}

/** Nivel de color según la precisión (0-100): se usa en barras y en el % de cada fila. */
function claseBarra(precision) {
    if (precision < 60) return "nivel-bajo";
    if (precision < 80) return "nivel-medio";
    return "nivel-alto";
}


// ------------------------------------------------------------------
// Pestaña 1: última práctica
// ------------------------------------------------------------------
function pintarUltima(datos) {
    const u = datos.ultima;

    const nombreTaller = document.getElementById("resultadoTaller");
    if (nombreTaller) {
        nombreTaller.textContent = "Última práctica: " +
            (u.nombre_taller || "Práctica") + " · " + u.nombre_area;
    }

    // ----- Tarjetas KPI -----
    document.getElementById("kpiCorrectas").textContent = u.respuestas_correctas;
    document.getElementById("kpiIncorrectas").textContent = u.respuestas_incorrectas;
    document.getElementById("kpiPrecision").textContent = Math.round(u.porcentaje) + "%";
    document.getElementById("kpiPreguntas").textContent = u.preguntas_totales;

    // ----- Dona -----
    const porcentaje = Math.max(0, Math.min(100, u.porcentaje));
    document.getElementById("donaRelleno").setAttribute(
        "stroke-dasharray",
        (porcentaje / 100 * CIRCUNFERENCIA_DONA).toFixed(2) + " " + CIRCUNFERENCIA_DONA
    );
    document.getElementById("donaPorcentaje").textContent = Math.round(porcentaje) + "%";
    document.getElementById("leyendaCorrectas").textContent = u.respuestas_correctas;
    document.getElementById("leyendaIncorrectas").textContent = u.respuestas_incorrectas;
    document.querySelector(".dona").setAttribute(
        "aria-label",
        Math.round(porcentaje) + " por ciento de respuestas correctas"
    );

    // ----- Barras por área -----
    document.getElementById("barrasAreas").innerHTML = datos.por_area
        .map(function (fila) {
            const ancho = Math.max(0, Math.min(100, Number(fila.porcentaje)));
            return (
                '<div class="barra-item">' +
                "<span>" + escResultado(fila.nombre_area) + " <b>" + ancho + "%</b></span>" +
                '<div class="barra-pista"><div class="barra-lleno" style="width: ' + ancho + '%;"></div></div>' +
                "</div>"
            );
        })
        .join("");

    // ----- Detalle de las incorrectas -----
    const bloqueDetalle = document.getElementById("bloqueDetalle");
    const contenedor = document.getElementById("detallePreguntas");

    if (!datos.incorrectas.length) {
        bloqueDetalle.innerHTML =
            '<p class="resultado-perfecto">🎉 ¡Ninguna pregunta incorrecta en esta práctica!</p>';
        return;
    }

    contenedor.innerHTML = datos.incorrectas
        .map(function (item) {
            const tema = item.tema || item.modulo || item.enunciado;
            return (
                '<details class="error-item">' +
                "<summary>Pregunta " + item.numero_pregunta + " · " + escResultado(tema) +
                ' <span class="etiqueta-respuesta mala">✗ Incorrecta</span></summary>' +
                '<div class="error-cuerpo">' +
                "<p><strong>Pregunta:</strong> " + escResultado(item.enunciado) + "</p>" +
                '<p><span class="etiqueta-respuesta mala">Tu respuesta</span> ' +
                escResultado(item.letra_elegida) + ") " + escResultado(item.texto_elegida) + "</p>" +
                '<p><span class="etiqueta-respuesta buena">Respuesta correcta</span> ' +
                escResultado(item.letra_correcta) + ") " + escResultado(item.texto_correcta) + "</p>" +
                '<p class="explicacion">' + escResultado(item.retroalimentacion) + "</p>" +
                "</div>" +
                "</details>"
            );
        })
        .join("");
}


// ------------------------------------------------------------------
// Pestañas
// ------------------------------------------------------------------
function prepararPestanas() {
    const subtitulo = document.getElementById("subtitulo");
    const botones = document.querySelectorAll(".pestana");

    function activar(boton) {
        const nombre = boton.dataset.pestana;

        botones.forEach(function (otro) {
            const activo = otro === boton;
            otro.classList.toggle("activa", activo);
            otro.setAttribute("aria-selected", activo ? "true" : "false");
            document.getElementById(otro.getAttribute("aria-controls")).hidden = !activo;
        });

        if (subtitulo) {
            subtitulo.textContent = SUBTITULOS[nombre] || SUBTITULOS.ultima;
        }

        if (nombre === "historial" || nombre === "temas") {
            cargarHistorial();
        }
    }

    botones.forEach(function (boton) {
        boton.addEventListener("click", function () {
            activar(boton);
            // Enlace profundo: praticar.html#historial o #temas
            if (window.history && history.replaceState) {
                history.replaceState(null, "", "#" + boton.dataset.pestana);
            }
        });
    });

    const marcada = location.hash.slice(1);
    if (Object.prototype.hasOwnProperty.call(SUBTITULOS, marcada)) {
        const boton = document.querySelector(
            '.pestana[data-pestana="' + marcada + '"]'
        );
        if (boton) activar(boton);
    }

    // "toggle" no burbujea, así que se escucha en la fase de captura.
    // Cada fila carga su detalle la primera vez que se abre.
    document.getElementById("histLista").addEventListener("toggle", function (evento) {
        const fila = evento.target;
        if (fila.tagName === "DETAILS" && fila.open) {
            abrirDetalle(fila);
        }
    }, true);
}


// ------------------------------------------------------------------
// Pestañas 2 y 3: historial y desempeño por tema
// ------------------------------------------------------------------
async function cargarHistorial() {
    if (cacheHistorial || cargandoHistorial) return;
    cargandoHistorial = true;

    const lista = document.getElementById("histLista");
    const vacio = document.getElementById("histVacio");
    const paginacion = document.getElementById("histPaginacion");

    lista.hidden = false;
    vacio.hidden = true;
    paginacion.hidden = true;
    lista.innerHTML = '<p class="cargando">Cargando historial…</p>';

    const datos = await apiGET("historial?pagina=1");

    if (!datos.ok) {
        cargandoHistorial = false;
        lista.innerHTML = "";
        vacio.hidden = false;
        return;
    }

    cargandoHistorial = false;
    cacheHistorial = datos;
    paginaActual = datos.pagina;
    areaActual = "";

    pintarFiltros(datos);
    pintarTemas(datos);
    pintarLista(datos);
    prepararPaginacion();
}

async function refrescarHistorial() {
    const lista = document.getElementById("histLista");
    lista.innerHTML = '<p class="cargando">Cargando…</p>';

    let ruta = "historial?pagina=" + paginaActual;
    if (areaActual) ruta += "&area=" + areaActual;

    const datos = await apiGET(ruta);
    if (!datos.ok) {
        lista.innerHTML = '<p class="cargando">No se pudo cargar el historial.</p>';
        return;
    }

    // La lista cambia de página/filtro; las áreas y los temas son globales
    // y se conservan de la primera respuesta.
    cacheHistorial.historial = datos.historial;
    cacheHistorial.total = datos.total;
    cacheHistorial.pagina = datos.pagina;
    cacheHistorial.paginas = datos.paginas;
    pintarLista(cacheHistorial);
}

/** Chips con las áreas que tienen al menos una práctica. */
function pintarFiltros(datos) {
    const caja = document.getElementById("histFiltros");
    if (!caja) return;

    if (!datos.areas.length) {
        caja.hidden = true;
        return;
    }

    const chips = [
        '<button type="button" class="chip-area activo" data-area="" aria-pressed="true">Todas</button>',
    ].concat(
        datos.areas.map(function (area) {
            return (
                '<button type="button" class="chip-area" data-area="' + area.id_area +
                '" aria-pressed="false">' + escResultado(area.nombre_area) + "</button>"
            );
        })
    );

    caja.innerHTML = chips.join("");
    caja.hidden = false;

    caja.querySelectorAll(".chip-area").forEach(function (chip) {
        chip.addEventListener("click", function () {
            if (chip.dataset.area === areaActual) return;
            areaActual = chip.dataset.area;
            paginaActual = 1;

            caja.querySelectorAll(".chip-area").forEach(function (otro) {
                const activo = otro === chip;
                otro.classList.toggle("activo", activo);
                otro.setAttribute("aria-pressed", activo ? "true" : "false");
            });

            refrescarHistorial();
        });
    });
}

function pintarLista(datos) {
    const lista = document.getElementById("histLista");
    const vacio = document.getElementById("histVacio");

    if (!datos.historial.length) {
        lista.innerHTML = "";
        lista.hidden = true;
        vacio.hidden = false;
        document.getElementById("histPaginacion").hidden = true;
        return;
    }

    lista.hidden = false;
    vacio.hidden = true;

    lista.innerHTML = datos.historial
        .map(function (fila) {
            const marcador = fila.respuestas_correctas + "/" + fila.preguntas_totales;
            const clase = claseBarra(Number(fila.porcentaje));
            return (
                '<details class="hist-item" data-id="' + fila.id_resultado + '">' +
                '<summary class="hist-resumen">' +
                '<span class="hist-fecha">' + escResultado(fechaLegible(fila.fecha_practica)) + "</span>" +
                '<span class="hist-area">' + escResultado(fila.nombre_area) + "</span>" +
                '<span class="hist-area">' + escResultado(fila.nombre_taller || "Práctica") + "</span>" +
                '<span class="hist-marcador">' + marcador + " correctas</span>" +
                '<span class="hist-porcentaje ' + clase + '">' +
                Math.round(fila.porcentaje) + "%</span>" +
                "</summary>" +
                '<div class="hist-detalle">Abriendo…</div>' +
                "</details>"
            );
        })
        .join("");

    const paginacion = document.getElementById("histPaginacion");
    paginacion.hidden = datos.paginas <= 1;
    document.getElementById("pagInfo").textContent =
        "Página " + datos.pagina + " de " + datos.paginas + " · " + datos.total + " prácticas";
    document.getElementById("pagAnterior").disabled = datos.pagina <= 1;
    document.getElementById("pagSiguiente").disabled = datos.pagina >= datos.paginas;
}

function prepararPaginacion() {
    document.getElementById("pagAnterior").addEventListener("click", function () {
        if (paginaActual <= 1) return;
        paginaActual -= 1;
        refrescarHistorial();
    });

    document.getElementById("pagSiguiente").addEventListener("click", function () {
        if (!cacheHistorial || paginaActual >= cacheHistorial.paginas) return;
        paginaActual += 1;
        refrescarHistorial();
    });
}

/** Detalle perezoso: se pide al abrir la fila y no se repite. */
async function abrirDetalle(detalle) {
    const caja = detalle.querySelector(".hist-detalle");
    if (!caja || detalle.dataset.cargado === "1") return;

    detalle.dataset.cargado = "1";
    caja.textContent = "Cargando…";

    const datos = await apiGET("historial/" + detalle.dataset.id);

    if (!datos.ok) {
        detalle.dataset.cargado = "";
        caja.textContent = "No se pudo cargar el detalle de esta práctica.";
        return;
    }

    if (!datos.respuestas.length) {
        caja.innerHTML = '<p class="cargando">Esta práctica no tiene respuestas registradas.</p>';
        return;
    }

    caja.innerHTML = datos.respuestas
        .map(function (item) {
            const etiqueta = item.es_correcta
                ? '<span class="etiqueta-respuesta buena">✓ Correcta</span> '
                : '<span class="etiqueta-respuesta mala">✗ Incorrecta</span> ';
            const correcta = item.es_correcta
                ? ""
                : '<p><span class="etiqueta-respuesta buena">Respuesta correcta</span> ' +
                  escResultado(item.letra_correcta) + ") " + escResultado(item.texto_correcta) + "</p>";

            return (
                '<div class="hist-pregunta">' +
                '<p class="hist-enunciado"><b>Pregunta ' + item.numero_pregunta + ".</b> " +
                escResultado(item.enunciado) + "</p>" +
                "<p>" + etiqueta +
                escResultado(item.letra_elegida) + ") " + escResultado(item.texto_elegida) + "</p>" +
                correcta +
                '<p class="explicacion">' + escResultado(item.retroalimentacion) + "</p>" +
                "</div>"
            );
        })
        .join("");
}

/** Barras por módulo/tema, de la más débil a la más fuerte. */
function pintarTemas(datos) {
    const caja = document.getElementById("barrasTemas");
    const vacio = document.getElementById("temasVacio");
    const nota = document.querySelector("#panel-temas .hist-nota");
    const grafica = document.querySelector("#panel-temas .grafica-caja");

    if (!datos.temas.length) {
        caja.innerHTML = "";
        if (grafica) grafica.hidden = true;
        if (nota) nota.hidden = true;
        vacio.hidden = false;
        return;
    }

    if (grafica) grafica.hidden = false;
    if (nota) nota.hidden = false;
    vacio.hidden = true;

    caja.innerHTML = datos.temas
        .map(function (tema) {
            const ancho = Math.max(0, Math.min(100, Number(tema.precision)));
            const refuerzo = ancho < 60
                ? ' <em class="badge-aviso">Reforzar</em>'
                : "";
            const respuestas = tema.respondidas + " respuesta" +
                (tema.respondidas === 1 ? "" : "s");

            return (
                '<div class="barra-item">' +
                "<span>" + escResultado(tema.tema) + " <b>" + ancho + "%</b></span>" +
                '<div class="barra-pista"><div class="barra-lleno ' + claseBarra(ancho) +
                '" style="width: ' + ancho + '%;"></div></div>' +
                '<small class="barra-meta">' + escResultado(tema.modulo) +
                " · " + respuestas + refuerzo + "</small>" +
                "</div>"
            );
        })
        .join("");
}


// ------------------------------------------------------------------
// Arranque
// ------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", async function () {
    const vacio = document.getElementById("vacio");
    const cuerpo = document.getElementById("cuerpo");
    if (!cuerpo) return;

    const datos = await apiGET("resultados");
    if (!datos.ok) return; // Sin sesión api.js ya redirigió.

    if (!datos.hay_datos) {
        vacio.hidden = false;
        return;
    }

    cuerpo.hidden = false;
    pintarUltima(datos);
    prepararPestanas();
});
