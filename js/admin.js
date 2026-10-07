/*
 * NIVELSABER - Panel de administración.
 *
 * Solo entra quien tenga rol 'admin' (se decide al iniciar sesión).
 * Habla con estas rutas del servidor:
 *   GET    /api/admin/preguntas?area=N  -> banco completo (con respuestas)
 *   POST   /api/admin/preguntas         -> crea una pregunta
 *   PUT    /api/admin/preguntas/N       -> edita una pregunta
 *   DELETE /api/admin/preguntas/N       -> elimina una pregunta
 *   GET    /api/admin/areas/N           -> detalle del área (resumen + respuestas)
 *   GET    /api/admin/usuarios          -> cuentas registradas con su actividad
 */

let preguntasActuales = [];   // Preguntas del área mostrada
let idPreguntaEditando = null; // null = el formulario crea una pregunta nueva

/* Igual que en script.js: evita que el texto del banco rompa el HTML. */


/* ------------------------------------------------------------------
 * Arranque: solo administradores
 * ------------------------------------------------------------------ */
document.addEventListener("DOMContentLoaded", async function () {
    const sesion = await apiGET("sesion");
    const rol = String(sesion.usuario && sesion.usuario.rol || "").trim().toLowerCase();
    if (!sesion.ok || !sesion.usuario || rol !== "admin") {
        const destino = sesion.usuario && rol === "estudiante"
            ? RAIZ + "index.html"
            : RAIZ + "login.html";
        location.replace(destino);
        return;
    }

    // Rol admin confirmado: ya se puede mostrar el panel (la hoja de
    // estilos lo mantiene oculto hasta este punto).
    document.documentElement.classList.add("rol-verificado");

    document.getElementById("formArea").addEventListener("submit", crearArea);
    document.getElementById("btnCerrarSesion").addEventListener("click", cerrarSesion);
    await cargarAreas();

    document.getElementById("selArea").addEventListener("change", cargarPreguntas);
    document.getElementById("btnNueva").addEventListener("click", abrirFormularioNueva);
    document.getElementById("btnCancelar").addEventListener("click", cerrarFormulario);
    document.getElementById("formulario").addEventListener("submit", guardarFormulario);

    // Secciones de la barra lateral izquierda.
    document.querySelectorAll("[data-pestana]").forEach(function (enlace) {
        enlace.addEventListener("click", function (evento) {
            evento.preventDefault();
            mostrarPestana(enlace.dataset.pestana);
        });
    });

    // Sección "Detalle del área" (barra lateral).
    document.getElementById("selAreaDetalle").addEventListener("change", cargarDetalleArea);
    document.getElementById("btnActualizarDetalle").addEventListener("click", cargarDetalleArea);

    // Sección "Estudiantes" (barra lateral).
    document.getElementById("selRolUsuarios").addEventListener("change", cargarEstudiantes);
    document.getElementById("btnActualizarEstudiantes").addEventListener("click", cargarEstudiantes);
});

async function cargarAreas(idSeleccionado) {
    const datos = await apiGET("areas");
    const selector = document.getElementById("selArea");

    if (!datos.ok) {
        selector.innerHTML = "<option>" + esc(datos.error) + "</option>";
        document.getElementById("listaAreas").textContent = datos.error;
        return;
    }

    pintarAreas(datos.areas);
    const seleccionAnterior = idSeleccionado === undefined
        ? selector.value
        : String(idSeleccionado);
    document.getElementById("btnNueva").disabled = datos.areas.length === 0;
    selector.innerHTML = datos.areas
        .map(function (area) {
            return '<option value="' + area.id_area + '">' + esc(area.nombre_area) + "</option>";
        })
        .join("");

    // El selector de la pestaña "Detalle del área" se mantiene al día.
    const selectorDetalle = document.getElementById("selAreaDetalle");
    const detalleAnterior = selectorDetalle.value;
    selectorDetalle.innerHTML = selector.innerHTML;
    if (datos.areas.some(function (area) { return String(area.id_area) === detalleAnterior; })) {
        selectorDetalle.value = detalleAnterior;
    }
    if (!datos.areas.length) {
        document.getElementById("listaPreguntas").innerHTML =
            '<p class="admin-vacio">Crea un área para empezar a agregar preguntas.</p>';
        return;
    }
    if (datos.areas.some(function (area) { return String(area.id_area) === seleccionAnterior; })) {
        selector.value = seleccionAnterior;
    }

    await cargarPreguntas();
}

function pintarAreas(areas) {
    const lista = document.getElementById("listaAreas");
    if (!areas.length) {
        lista.innerHTML = '<p class="admin-vacio">No hay áreas creadas.</p>';
        return;
    }

    lista.innerHTML = areas.map(function (area) {
        return (
            '<div class="admin-area-item">' +
            '<span><strong>' + esc(area.nombre_area) + '</strong> · ' +
            Number(area.preguntas) + ' preguntas</span>' +
            '<div class="admin-botones">' +
            '<button type="button" class="admin-btn" data-editar-area="' + area.id_area + '">Renombrar</button>' +
            '<button type="button" class="admin-btn peligro" data-borrar-area="' + area.id_area + '">Eliminar</button>' +
            '</div></div>'
        );
    }).join("");

    lista.querySelectorAll("[data-editar-area]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const area = areas.find(function (item) {
                return item.id_area === Number(boton.dataset.editarArea);
            });
            if (area) editarArea(area);
        });
    });

    lista.querySelectorAll("[data-borrar-area]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const area = areas.find(function (item) {
                return item.id_area === Number(boton.dataset.borrarArea);
            });
            if (area) eliminarArea(area);
        });
    });
}

async function crearArea(evento) {
    evento.preventDefault();
    const campo = document.getElementById("nombreArea");
    const nombre = campo.value.trim();
    const datos = await apiPOST("admin/areas", { nombre_area: nombre });
    if (!datos.ok) {
        mostrarMensajeArea(datos.error, "error");
        return;
    }

    campo.value = "";
    mostrarMensajeArea(datos.mensaje, "exito");
    await cargarAreas(datos.id_area);
}

async function editarArea(area) {
    const nombre = prompt("Nuevo nombre para el área:", area.nombre_area);
    if (nombre === null) return;

    const datos = await apiPUT("admin/areas/" + area.id_area, { nombre_area: nombre.trim() });
    if (!datos.ok) {
        mostrarMensajeArea(datos.error, "error");
        return;
    }

    mostrarMensajeArea(datos.mensaje, "exito");
    await cargarAreas();
}

async function eliminarArea(area) {
    if (!confirm(
        '¿Eliminar el área "' + area.nombre_area + '"? Solo se puede eliminar si no tiene preguntas ni resultados.'
    )) return;

    const datos = await apiDEL("admin/areas/" + area.id_area);
    if (!datos.ok) {
        mostrarMensajeArea(datos.error, "error");
        return;
    }

    mostrarMensajeArea(datos.mensaje, "exito");
    await cargarAreas();
}

async function cerrarSesion() {
    const boton = document.getElementById("btnCerrarSesion");
    boton.disabled = true;
    const datos = await apiPOST("logout", {});
    if (!datos.ok) {
        boton.disabled = false;
        mostrarMensajeArea(datos.error || "No se pudo cerrar la sesión.", "error");
        return;
    }
    location.href = RAIZ + "login.html";
}

function mostrarMensajeArea(texto, tipo) {
    const caja = document.getElementById("mensajeArea");
    caja.textContent = texto;
    caja.className = tipo ? "mensaje " + tipo : "mensaje";
}

/* ------------------------------------------------------------------
 * Lista de preguntas del área elegida
 * ------------------------------------------------------------------ */
async function cargarPreguntas() {
    const idArea = document.getElementById("selArea").value;
    const lista = document.getElementById("listaPreguntas");
    if (!idArea) {
        lista.innerHTML = '<p class="admin-vacio">Selecciona un área.</p>';
        return;
    }

    lista.innerHTML = '<p class="admin-vacio">Cargando preguntas…</p>';

    const datos = await apiGET("admin/preguntas?area=" + encodeURIComponent(idArea));
    if (!datos.ok) {
        lista.innerHTML = '<p class="admin-vacio">' + esc(datos.error) + "</p>";
        return;
    }

    preguntasActuales = datos.preguntas;
    pintarPreguntas();
}

function pintarPreguntas() {
    const lista = document.getElementById("listaPreguntas");

    if (!preguntasActuales.length) {
        lista.innerHTML = '<p class="admin-vacio">Esta área todavía no tiene preguntas.</p>';
        return;
    }

    lista.innerHTML = preguntasActuales
        .map(function (pregunta) {
            const correcta = pregunta.opciones.find(function (o) { return o.correcta; });
            return (
                '<div class="admin-tarjeta">' +
                '<p class="admin-num">Pregunta ' + pregunta.numero + "</p>" +
                '<p class="admin-enunciado">' + esc(pregunta.enunciado) + "</p>" +
                '<p class="admin-tema">' + esc(pregunta.modulo) + " · " + esc(pregunta.tema) + "</p>" +
                (correcta
                    ? '<p class="admin-correcta">✔ ' + esc(correcta.letra + ") " + correcta.texto) + "</p>"
                    : "") +
                '<div class="admin-botones">' +
                '<button type="button" class="admin-btn" data-editar="' + pregunta.id_pregunta + '">Editar</button>' +
                '<button type="button" class="admin-btn peligro" data-borrar="' + pregunta.id_pregunta + '">Eliminar</button>' +
                "</div>" +
                "</div>"
            );
        })
        .join("");

    // Conecta los botones de cada tarjeta con sus funciones.
    lista.querySelectorAll("[data-editar]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            abrirFormularioEdicion(Number(boton.dataset.editar));
        });
    });

    lista.querySelectorAll("[data-borrar]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            eliminarPregunta(Number(boton.dataset.borrar));
        });
    });
}

/* ------------------------------------------------------------------
 * Formulario de crear / editar
 * ------------------------------------------------------------------ */
function abrirFormularioNueva() {
    idPreguntaEditando = null;
    document.getElementById("tituloFormulario").textContent = "Nueva pregunta";
    limpiarFormulario();
    document.getElementById("formulario").hidden = false;
    document.getElementById("fEnunciado").focus();
}

function abrirFormularioEdicion(idPregunta) {
    const pregunta = preguntasActuales.find(function (p) { return p.id_pregunta === idPregunta; });
    if (!pregunta) return;

    idPreguntaEditando = idPregunta;
    document.getElementById("tituloFormulario").textContent =
        "Editar pregunta " + pregunta.numero;

    limpiarFormulario();
    document.getElementById("fEnunciado").value = pregunta.enunciado || "";
    document.getElementById("fModulo").value = pregunta.modulo || "";
    document.getElementById("fTema").value = pregunta.tema || "";
    document.getElementById("fRetro").value = pregunta.retroalimentacion || "";

    pregunta.opciones.forEach(function (opcion, posicion) {
        document.getElementById("fOpcion" + posicion).value = opcion.texto || "";
        if (opcion.correcta) {
            document.getElementById("correcta" + posicion).checked = true;
        }
    });

    document.getElementById("formulario").hidden = false;
    document.getElementById("fEnunciado").focus();
}

function limpiarFormulario() {
    document.getElementById("formulario").reset();
    mostrarMensajeFormulario("", "");
}

function cerrarFormulario() {
    idPreguntaEditando = null;
    document.getElementById("formulario").hidden = true;
}

/* Lee el formulario y lo envía a crear o editar según el caso. */
async function guardarFormulario(evento) {
    evento.preventDefault();

    const marcada = document.querySelector("input[name=correcta]:checked");
    if (!marcada) {
        mostrarMensajeFormulario("Marca cuál opción es la correcta.", "error");
        return;
    }

    const opciones = [0, 1, 2, 3].map(function (posicion) {
        return {
            texto: document.getElementById("fOpcion" + posicion).value.trim(),
            correcta: marcada.value === String(posicion),
        };
    }).filter(function (opcion) {
        return opcion.texto;
    });

    if (opciones.length < 2) {
        mostrarMensajeFormulario("Escribe al menos dos opciones.", "error");
        return;
    }
    if (!opciones.some(function (opcion) { return opcion.correcta; })) {
        mostrarMensajeFormulario("La opción marcada como correcta debe tener texto.", "error");
        return;
    }

    const cuerpo = {
        id_area: Number(document.getElementById("selArea").value),
        enunciado: document.getElementById("fEnunciado").value.trim(),
        modulo: document.getElementById("fModulo").value.trim(),
        tema: document.getElementById("fTema").value.trim(),
        retroalimentacion: document.getElementById("fRetro").value.trim(),
        opciones: opciones,
    };

    const datos = idPreguntaEditando === null
        ? await apiPOST("admin/preguntas", cuerpo)
        : await apiPUT("admin/preguntas/" + idPreguntaEditando, cuerpo);

    if (!datos.ok) {
        mostrarMensajeFormulario(datos.error, "error");
        return;
    }

    mostrarMensajeFormulario(datos.mensaje, "exito");
    await cargarPreguntas();
    setTimeout(cerrarFormulario, 600);
}

async function eliminarPregunta(idPregunta) {
    const pregunta = preguntasActuales.find(function (p) { return p.id_pregunta === idPregunta; });
    const confirmar = confirm(
        "¿Eliminar la pregunta " + (pregunta ? pregunta.numero : idPregunta) + "?\n" +
        "También se borran sus opciones y las respuestas de los estudiantes."
    );
    if (!confirmar) return;

    const datos = await apiDEL("admin/preguntas/" + idPregunta);
    if (!datos.ok) {
        alert(datos.error);
        return;
    }

    await cargarPreguntas();
}

function mostrarMensajeFormulario(texto, tipo) {
    const caja = document.getElementById("mensajeFormulario");
    if (!caja) return;
    caja.textContent = texto;
    caja.className = tipo ? "mensaje " + tipo : "mensaje";
}

/* ------------------------------------------------------------------
 * Secciones del panel (se cambian desde la barra lateral)
 * ------------------------------------------------------------------ */
function mostrarPestana(nombre) {
    // Marca la sección activa en la barra lateral.
    document.querySelectorAll("[data-pestana]").forEach(function (enlace) {
        enlace.classList.toggle("active", enlace.dataset.pestana === nombre);
    });

    document.getElementById("pestanaBanco").hidden = nombre !== "banco";
    document.getElementById("pestanaDetalle").hidden = nombre !== "detalle";
    document.getElementById("pestanaEstudiantes").hidden = nombre !== "estudiantes";

    if (nombre === "detalle") cargarDetalleArea();
    if (nombre === "estudiantes") cargarEstudiantes();
}

/* ------------------------------------------------------------------
 * Sección "Detalle del área": resumen, preguntas, opciones y respuestas
 * ------------------------------------------------------------------ */
async function cargarDetalleArea() {
    const contenedor = document.getElementById("detalleArea");
    const idArea = document.getElementById("selAreaDetalle").value;

    if (!idArea) {
        contenedor.innerHTML = '<p class="admin-vacio">Crea un área para poder ver su detalle.</p>';
        return;
    }

    contenedor.innerHTML = '<p class="admin-vacio">Cargando el detalle del área…</p>';

    const datos = await apiGET("admin/areas/" + encodeURIComponent(idArea));
    if (!datos.ok) {
        contenedor.innerHTML = '<p class="admin-vacio">' + esc(datos.error) + "</p>";
        return;
    }

    pintarDetalleArea(datos);
}

function pintarDetalleArea(datos) {
    const contenedor = document.getElementById("detalleArea");
    const resumen = datos.resumen;

    const kpis = [
        ["Preguntas", resumen.preguntas],
        ["Opciones", resumen.opciones],
        ["Prácticas", resumen.practicas],
        ["Estudiantes", resumen.estudiantes],
        ["Respuestas", resumen.respondidas],
        ["Precisión", resumen.precision === null ? "—" : resumen.precision + "%"],
    ];

    let html = '<div class="admin-kpis">' + kpis.map(function (kpi) {
        return (
            '<div class="admin-kpi">' +
            '<span class="admin-kpi-valor">' + esc(kpi[1]) + "</span>" +
            '<span class="admin-kpi-etiqueta">' + esc(kpi[0]) + "</span>" +
            "</div>"
        );
    }).join("") + "</div>";

    html += '<p class="admin-subtitulo">Banco de preguntas de ' +
        esc(datos.area.nombre_area) + "</p>";

    if (!datos.preguntas.length) {
        html += '<p class="admin-vacio">Este área todavía no tiene preguntas.</p>';
        contenedor.innerHTML = html;
        return;
    }

    html += datos.preguntas.map(function (pregunta) {
        const respuestas = pregunta.respuestas;
        const precision = respuestas.precision === null
            ? "sin respuestas"
            : respuestas.precision + "% de aciertos";

        let tarjeta = '<div class="admin-tarjeta">';
        tarjeta += '<p class="admin-num">Pregunta ' + pregunta.numero + " · " +
            respuestas.respondidas + " respuestas de " + respuestas.estudiantes +
            " estudiante(s) · " + precision + "</p>";
        tarjeta += '<p class="admin-enunciado">' + esc(pregunta.enunciado) + "</p>";
        tarjeta += '<p class="admin-tema">' + esc(pregunta.modulo) + " · " +
            esc(pregunta.tema) + "</p>";

        // Todas las opciones con cuántas veces fueron elegidas.
        tarjeta += '<ul class="admin-opciones-detalle">' +
            pregunta.opciones.map(function (opcion) {
                const elegidas = (pregunta.elegidas || {})[opcion.letra] || 0;
                return (
                    '<li class="' + (opcion.correcta ? "correcta" : "") + '">' +
                    '<span class="letra">' + esc(opcion.letra) + ")</span>" +
                    '<span class="texto">' + esc(opcion.texto) + "</span>" +
                    '<span class="conteo">' + elegidas +
                    (elegidas === 1 ? " respuesta" : " respuestas") + "</span>" +
                    (opcion.correcta ? '<span class="marca">✔ correcta</span>' : "") +
                    "</li>"
                );
            }).join("") + "</ul>";

        if (pregunta.retroalimentacion) {
            tarjeta += '<p class="admin-retro"><strong>Retroalimentación:</strong> ' +
                esc(pregunta.retroalimentacion) + "</p>";
        }

        tarjeta += "</div>";
        return tarjeta;
    }).join("");

    contenedor.innerHTML = html;
}

/* ------------------------------------------------------------------
 * Sección "Estudiantes": cuentas registradas con su actividad
 * ------------------------------------------------------------------ */
async function cargarEstudiantes() {
    const contenedor = document.getElementById("listaEstudiantes");
    contenedor.innerHTML = '<p class="admin-vacio">Cargando cuentas…</p>';

    const datos = await apiGET("admin/usuarios");
    if (!datos.ok) {
        contenedor.innerHTML = '<p class="admin-vacio">' + esc(datos.error) + "</p>";
        return;
    }

    const rolFiltro = document.getElementById("selRolUsuarios").value;
    const usuarios = datos.usuarios.filter(function (usuario) {
        return !rolFiltro || String(usuario.rol || "").trim().toLowerCase() === rolFiltro;
    });

    pintarEstudiantes(usuarios);
}

/* "2026-10-06 18:30" -> "06/10/2026 18:30" */
function fechaCorta(valor) {
    const partes = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/.exec(String(valor || ""));
    if (!partes) return valor ? String(valor) : "—";
    return partes[3] + "/" + partes[2] + "/" + partes[1] + " " + partes[4] + ":" + partes[5];
}

function pintarEstudiantes(usuarios) {
    const contenedor = document.getElementById("listaEstudiantes");
    document.getElementById("cuentaUsuarios").textContent =
        usuarios.length + (usuarios.length === 1 ? " cuenta" : " cuentas");

    if (!usuarios.length) {
        contenedor.innerHTML = '<p class="admin-vacio">No hay cuentas para ese filtro.</p>';
        return;
    }

    contenedor.innerHTML =
        '<div class="admin-tabla-envoltura"><table class="admin-tabla">' +
        "<thead><tr>" +
        "<th>Nombre</th><th>Correo</th><th>Rol</th><th>Registro</th>" +
        "<th>Prácticas</th><th>Precisión</th><th>Última práctica</th>" +
        "</tr></thead><tbody>" +
        usuarios.map(function (usuario) {
            const nombre = [usuario.nombre, usuario.apellido].filter(Boolean).join(" ");
            const rol = String(usuario.rol || "").trim().toLowerCase() || "sin rol";
            const precision = usuario.precision === null ? "—" : usuario.precision + "%";
            return (
                "<tr>" +
                '<td data-label="Nombre">' + esc(nombre) + "</td>" +
                '<td data-label="Correo">' + esc(usuario.correo) + "</td>" +
                '<td data-label="Rol"><span class="admin-chip ' + esc(rol) + '">' +
                esc(rol) + "</span></td>" +
                '<td data-label="Registro">' + esc(fechaCorta(usuario.fecha_registro)) + "</td>" +
                '<td data-label="Prácticas">' + Number(usuario.practicas) + "</td>" +
                '<td data-label="Precisión">' + precision + "</td>" +
                '<td data-label="Última práctica">' +
                esc(fechaCorta(usuario.ultima_practica)) + "</td>" +
                "</tr>"
            );
        }).join("") +
        "</tbody></table></div>";
}
