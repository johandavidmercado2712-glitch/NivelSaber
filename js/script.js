/*
 * NIVELSABER - Vista de práctica.
 *
 * Todo lo que se ve aquí viene de la base de datos a través de la API:
 *   GET  /api/areas      -> número real de preguntas de cada tarjeta
 *   GET  /api/preguntas  -> enunciado y opciones (sin la respuesta)
 *   POST /api/respuestas -> calificación y guardado del resultado
 */

let vistaSaludo = "";
let vistaAreas = "";

let areaActual = null;
let tallerActual = null;
let talleresActuales = [];
let datosAreas = [];
let vistaActual = "areas";
let preguntas = [];
let indice = 0;
let respuestas = {};

function esc(valor) {
    return String(valor === null || valor === undefined ? "" : valor)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

/* ------------------------------------------------------------------
 * Tarjetas: el conteo de preguntas lo pinta la API
 * ------------------------------------------------------------------ */
document.addEventListener("DOMContentLoaded", async function () {
    const grid = document.querySelector(".areas-grid");
    if (!grid) return;

    grid.addEventListener("click", function (evento) {
        const botonArea = evento.target.closest("[data-area]");
        if (botonArea) {
            const area = datosAreas.find(function (item) {
                return item.id_area === Number(botonArea.dataset.area);
            });
            if (area) seleccionarArea(area.id_area, area.nombre_area);
            return;
        }

        const botonTaller = evento.target.closest("[data-taller]");
        if (botonTaller) {
            const taller = talleresActuales.find(function (item) {
                return item.id_taller === botonTaller.dataset.taller;
            });
            if (taller) seleccionarTaller(taller);
        }
    });

    const datos = await apiGET("areas");
    if (!datos.ok) {
        grid.innerHTML = '<p class="practica-vacio">' + esc(datos.error) + "</p>";
        return;
    }

    const clases = ["area-lectura", "area-matematicas", "area-naturales", "area-sociales", "area-ingles"];
    const iconos = ["📖", "📐", "🔬", "🌍", "🗣️"];
    if (!datos.areas.length) {
        grid.innerHTML = '<p class="practica-vacio">No hay áreas disponibles por ahora.</p>';
        return;
    }

    datosAreas = datos.areas;
    grid.innerHTML = datos.areas.map(function (area, indice) {
        const n = Number(area.talleres || 0);
        const bancoAnterior = Number(area.preguntas_anteriores || 0) > 0;
        return (
            '<article class="tarjeta-area ' + clases[indice % clases.length] + '">' +
            '<span class="tarjeta-icono">' + iconos[indice % iconos.length] + "</span>" +
            "<h3>" + esc(area.nombre_area) + "</h3>" +
            '<span class="tarjeta-preguntas">' + (n === 1 ? "1 taller" : n + " talleres") +
            (bancoAnterior ? " · banco anterior" : "") + "</span>" +
            '<button type="button" class="btn-comenzar" data-area="' + Number(area.id_area) + '">' +
            "Ver talleres</button></article>"
        );
    }).join("");

});

/* ------------------------------------------------------------------
 * Entrar a un área
 * ------------------------------------------------------------------ */
async function seleccionarArea(idArea, nombreArea) {
    const saludo = document.querySelector(".saludo");
    const grid = document.querySelector(".areas-grid");
    if (!saludo || !grid) return;

    // Se guarda la vista de tarjetas justo aquí: ya contiene los conteos reales.
    vistaSaludo = saludo.innerHTML;
    vistaAreas = grid.innerHTML;
    mostrarBotonVolver();
    areaActual = { id: idArea, nombre: nombreArea };
    vistaActual = "talleres";

    saludo.innerHTML =
        "<h2>Talleres de " + esc(nombreArea) + "</h2>" +
        "<p>Elige una prueba para comenzar</p>";

    grid.innerHTML = '<p class="practica-cargando">Cargando talleres…</p>';

    const datos = await apiGET("talleres?area=" + encodeURIComponent(idArea));

    if (!datos.ok) {
        grid.innerHTML = '<p class="practica-vacio">' + esc(datos.error) + "</p>";
        return;
    }

    talleresActuales = datos.talleres;
    pintarTalleres();
}

function pintarTalleres() {
    const saludo = document.querySelector(".saludo");
    const grid = document.querySelector(".areas-grid");
    if (!saludo || !grid || !areaActual) return;

    saludo.innerHTML =
        "<h2>Talleres de " + esc(areaActual.nombre) + "</h2>" +
        "<p>Elige una prueba para comenzar</p>";

    if (!talleresActuales.length) {
        grid.innerHTML = '<p class="practica-vacio">Esta área todavía no tiene talleres.</p>';
        return;
    }

    grid.innerHTML = talleresActuales.map(function (taller) {
        const esAnterior = taller.id_taller === "__banco_anterior__";
        return (
            '<article class="tarjeta-area area-lectura">' +
            '<span class="tarjeta-icono">' + (esAnterior ? "📚" : "📝") + "</span>" +
            "<h3>" + esc(taller.nombre_taller) + "</h3>" +
            '<span class="tarjeta-preguntas">' + Number(taller.preguntas) +
            (Number(taller.preguntas) === 1 ? " pregunta" : " preguntas") + "</span>" +
            '<button type="button" class="btn-comenzar" data-taller="' +
            esc(taller.id_taller) + '">Comenzar</button></article>'
        );
    }).join("");

}

async function seleccionarTaller(taller) {
    const saludo = document.querySelector(".saludo");
    const grid = document.querySelector(".areas-grid");
    if (!saludo || !grid || !areaActual) return;

    tallerActual = taller;
    vistaActual = "practica";
    saludo.innerHTML =
        "<h2>" + esc(taller.nombre_taller) + "</h2>" +
        "<p>Práctica de " + esc(areaActual.nombre) + "</p>";
    grid.innerHTML =
        '<div class="practica" id="practica">' +
        '<p class="practica-cargando">Cargando preguntas…</p>' +
        "</div>";

    const datos = await apiGET(
        "preguntas?area=" + encodeURIComponent(areaActual.id) +
        "&taller=" + encodeURIComponent(taller.id_taller)
    );

    if (!datos.ok) {
        pintarEnPractica('<p class="practica-vacio">' + esc(datos.error) + "</p>");
        return;
    }

    preguntas = datos.preguntas;
    indice = 0;
    respuestas = {};
    pintarPregunta();
}

function pintarEnPractica(html) {
    const cont = document.getElementById("practica");
    if (cont) cont.innerHTML = html;
}

function cabeceraPregunta(actual, total) {
    const ancho = Math.round((actual / total) * 100);
    return (
        '<div class="practica-cabecera">' +
        '<p class="practica-titulo">' + esc(tallerActual.nombre_taller) + "</p>" +
        '<p class="practica-progreso">Pregunta ' + actual + " de " + total + "</p>" +
        '<div class="practica-barra"><div class="practica-barra-lleno" style="width: ' +
        ancho + '%;"></div></div>' +
        "</div>"
    );
}

/* ------------------------------------------------------------------
 * Dibujar la pregunta actual
 * ------------------------------------------------------------------ */
function pintarPregunta() {
    const pregunta = preguntas[indice];
    const total = preguntas.length;
    const ultima = indice === total - 1;

    const opciones = pregunta.opciones
        .map(function (opcion) {
            const marcada = respuestas[pregunta.id_pregunta] === opcion.id_opcion;
            return (
                '<label class="practica-opcion">' +
                '<input type="radio" name="pregunta_' + pregunta.id_pregunta +
                '" value="' + opcion.id_opcion + '"' + (marcada ? " checked" : "") + ">" +
                '<span class="letra">' + esc(opcion.letra) + "</span>" +
                '<span class="texto">' + esc(opcion.texto) + "</span>" +
                "</label>"
            );
        })
        .join("");

    const meta = [pregunta.modulo, pregunta.tema].filter(Boolean).map(esc).join(" · ");

    pintarEnPractica(
        cabeceraPregunta(indice + 1, total) +
        '<div class="practica-pregunta">' +
        '<p class="practica-meta">' + meta + "</p>" +
        '<p class="practica-enunciado">' + esc(pregunta.enunciado) + "</p>" +
        '<div class="practica-opciones">' + opciones + "</div>" +
        "</div>" +
        '<div class="practica-acciones">' +
        (indice > 0
            ? '<button type="button" class="practica-btn" id="btnAnterior">← Anterior</button>'
            : "<span></span>") +
        (ultima
            ? '<button type="button" class="practica-btn primario" id="btnEnviar">Enviar respuestas</button>'
            : '<button type="button" class="practica-btn primario" id="btnSiguiente">Siguiente →</button>') +
        "</div>"
    );

    const anterior = document.getElementById("btnAnterior");
    if (anterior) {
        anterior.addEventListener("click", function () {
            guardarActual();
            indice -= 1;
            pintarPregunta();
        });
    }

    const siguiente = document.getElementById("btnSiguiente");
    if (siguiente) {
        siguiente.addEventListener("click", function () {
            if (!guardarActual()) return;
            indice += 1;
            pintarPregunta();
        });
    }

    const enviar = document.getElementById("btnEnviar");
    if (enviar) enviar.addEventListener("click", enviarRespuestas);
}

/* Lee el radio marcado y devuelve false si todavía no hay respuesta. */
function guardarActual() {
    const marcado = document.querySelector("#practica input[type=radio]:checked");
    if (!marcado) {
        aviso("Elige una opción para continuar.");
        return false;
    }
    respuestas[preguntas[indice].id_pregunta] = Number(marcado.value);
    return true;
}

function aviso(mensaje) {
    const accion = document.getElementById("btnSiguiente") || document.getElementById("btnEnviar");
    const previo = document.getElementById("practicaAviso");
    if (previo) previo.remove();
    if (!accion) return;

    const caja = document.createElement("p");
    caja.className = "practica-aviso";
    caja.id = "practicaAviso";
    caja.textContent = mensaje;
    accion.closest(".practica-acciones").before(caja);
}

/* ------------------------------------------------------------------
 * Enviar la práctica al servidor
 * ------------------------------------------------------------------ */
async function enviarRespuestas() {
    if (!guardarActual()) return;

    const sinResponder = preguntas.filter(function (p) {
        return !respuestas[p.id_pregunta];
    });
    if (sinResponder.length) {
        // Se salta directamente a la primera que falta.
        indice = preguntas.indexOf(sinResponder[0]);
        pintarPregunta();
        aviso("Todavía faltan " + sinResponder.length +
              (sinResponder.length === 1 ? " pregunta." : " preguntas."));
        return;
    }

    const boton = document.getElementById("btnEnviar");
    boton.disabled = true;
    boton.textContent = "Enviando…";

    const datos = await apiPOST("respuestas", {
        id_area: areaActual.id,
        taller: tallerActual.id_taller,
        respuestas: preguntas.map(function (p) {
            return { id_pregunta: p.id_pregunta, id_opcion: respuestas[p.id_pregunta] };
        }),
    });

    if (!datos.ok) {
        boton.disabled = false;
        boton.textContent = "Enviar respuestas";
        aviso(datos.error);
        return;
    }

    pintarResultado(datos);
}

/* ------------------------------------------------------------------
 * Pantalla final con la revisión
 * ------------------------------------------------------------------ */
function pintarResultado(datos) {
    const r = datos.resultado;
    const total = r.preguntas_totales;
    const aciertos = r.respuestas_correctas;

    const veredicto = r.porcentaje >= 60
        ? { clase: "buena", texto: "¡Buen trabajo! Sigue así 🎉" }
        : r.porcentaje >= 40
            ? { clase: "regular", texto: "Vas por buen camino, repasa lo que falló" }
            : { clase: "mala", texto: "Toca repasar este área" };

    const revision = datos.detalle
        .map(function (item) {
            const estado = item.es_correcta ? "buena" : "mala";
            const marca = item.es_correcta ? "✓ Correcta" : "✗ Incorrecta";
            return (
                '<div class="practica-respuesta ' + estado + '">' +
                '<p><span class="practica-etiqueta ' + estado + '">' + marca + "</span>" +
                '<span class="pregunta-num">Pregunta ' + item.numero + "</span></p>" +
                '<p class="texto-enunciado">' + esc(item.enunciado) + "</p>" +
                (item.es_correcta
                    ? ""
                    : "<p><span class=\"practica-etiqueta mala\">Tu respuesta</span>" +
                      esc(item.elegida.letra) + ") " + esc(item.elegida.texto) + "</p>" +
                      "<p><span class=\"practica-etiqueta buena\">Correcta</span>" +
                      esc(item.correcta.letra) + ") " + esc(item.correcta.texto) + "</p>") +
                '<p class="practica-explicacion">' + esc(item.retroalimentacion) + "</p>" +
                "</div>"
            );
        })
        .join("");

    pintarEnPractica(
        '<div class="practica-resultado">' +
        "<h2>" + esc(r.nombre_taller || tallerActual.nombre_taller) + " terminada</h2>" +
        '<span class="practica-puntaje">' + r.porcentaje + "%</span>" +
        '<span class="practica-puntaje-detalle">' + aciertos +
        (aciertos === 1 ? " punto · " : " puntos · ") +
        r.respuestas_incorrectas + " incorrectas de " + total + "</span>" +
        '<span class="practica-veredicto ' + veredicto.clase + '">' + veredicto.texto + "</span>" +
        "</div>" +
        '<div class="practica-resumen">' + revision + "</div>" +
        '<div class="practica-finas">' +
        '<button type="button" class="practica-btn" id="btnRepetir">Practicar otra vez</button>' +
        '<a class="practica-btn primario" href="praticar.html" style="text-decoration:none;">' +
        "Ver todos mis resultados</a>" +
        "</div>"
    );

    const repetir = document.getElementById("btnRepetir");
    if (repetir) repetir.addEventListener("click", volverAtras);
}

/* ------------------------------------------------------------------
 * Volver a las tarjetas
 * ------------------------------------------------------------------ */
function mostrarBotonVolver() {
    const boton = document.getElementById("btnVolver");
    if (boton) boton.hidden = false;
}

function volverAtras() {
    if (vistaActual === "practica" && areaActual) {
        preguntas = [];
        respuestas = {};
        indice = 0;
        tallerActual = null;
        vistaActual = "talleres";
        pintarTalleres();
        return;
    }

    const saludo = document.querySelector(".saludo");
    const grid = document.querySelector(".areas-grid");
    if (saludo && grid) {
        saludo.innerHTML = vistaSaludo;
        grid.innerHTML = vistaAreas;
    }

    areaActual = null;
    tallerActual = null;
    talleresActuales = [];
    vistaActual = "areas";
    preguntas = [];
    respuestas = {};
    indice = 0;

    const boton = document.getElementById("btnVolver");
    if (boton) boton.hidden = true;
}

document.addEventListener("DOMContentLoaded", function () {
    const boton = document.getElementById("btnVolver");
    if (boton) boton.addEventListener("click", volverAtras);
});
