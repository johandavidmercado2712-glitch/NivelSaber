document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-toggle-password]").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const campo = document.getElementById(boton.dataset.togglePassword);
            if (!campo) return;

            const visible = campo.type === "password";
            campo.type = visible ? "text" : "password";
            boton.setAttribute("aria-pressed", String(visible));
            boton.setAttribute("aria-label", visible ? "Ocultar contraseña" : "Mostrar contraseña");
        });
    });

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (evento) {
            evento.preventDefault();

            const email = document.getElementById("email").value.trim().toLowerCase();
            const password = document.getElementById("password").value;

            const datos = await enviar("api/login", {
                email: email,
                password: password
            });

            if (!datos.ok) {
                mostrarMensaje(datos.error, "error");
                return;
            }

            mostrarMensaje("¡Bienvenido " + datos.usuario.nombre + "! Cargando...", "exito");
            const rol = String(datos.usuario.rol || "").trim().toLowerCase();
            if (rol !== "admin" && rol !== "estudiante") {
                mostrarMensaje(
                    "La cuenta no tiene un rol válido. Contacta al administrador del sistema.",
                    "error"
                );
                return;
            }
            const destino = rol === "admin"
                ? "barralateral/admin.html"
                : "index.html";

            setTimeout(function () {
                window.location.href = destino;
            }, 600);
        });
    }

    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", async function (evento) {
            evento.preventDefault();

            const nombre = document.getElementById("nombre").value.trim();
            const apellido = document.getElementById("apellido").value.trim();
            const email = document.getElementById("email").value.trim().toLowerCase();
            const password = document.getElementById("password").value;
            const confirmar = document.getElementById("confirm-password").value;

            if (!nombre || !apellido) {
                mostrarMensaje("Escribe tu nombre y tu apellido.", "error");
                return;
            }

            if (password !== confirmar) {
                mostrarMensaje("Las contraseñas no coinciden.", "error");
                return;
            }

            if (password.length < 6) {
                mostrarMensaje("La contraseña debe tener al menos 6 caracteres.", "error");
                return;
            }

            const datos = await enviar("api/registro", {
                nombre: nombre,
                apellido: apellido,
                email: email,
                password: password,
                confirm_password: confirmar
            });

            if (!datos.ok) {
                mostrarMensaje(datos.error, "error");
                return;
            }

            mostrarMensaje("Cuenta creada. Te llevamos al inicio de sesión...", "exito");

            setTimeout(function () {
                window.location.href = "login.html";
            }, 800);
        });
    }

    async function enviar(ruta, cuerpo) {
        try {
            const respuesta = await fetch(ruta, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "same-origin",
                body: JSON.stringify(cuerpo)
            });
            return await respuesta.json();
        } catch (error) {
            return { ok: false, error: "No se pudo conectar con el servidor. ¿Está corriendo?" };
        }
    }

    function mostrarMensaje(texto, tipo) {
        const caja = document.getElementById("mensaje");
        if (!caja) return;
        caja.textContent = texto;
        caja.className = "mensaje " + tipo;
        caja.style.display = "block";
    }
});
