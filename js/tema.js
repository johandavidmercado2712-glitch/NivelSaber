// Cambio de tema (claro / oscuro) con persistencia en localStorage
document.addEventListener('DOMContentLoaded', function () {

    function aplicarTema(tema) {
        document.documentElement.setAttribute('data-tema', tema);
        const boton = document.getElementById('btnTema');
        if (boton) {
            boton.textContent = tema === 'oscuro' ? '☀️' : '🌙';
            boton.title = tema === 'oscuro' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
        }
    }

    const guardado = localStorage.getItem('tema') || 'claro';
    aplicarTema(guardado);

    const botonTema = document.getElementById('btnTema');
    if (botonTema) {
        botonTema.addEventListener('click', function () {
            const actual = document.documentElement.getAttribute('data-tema') === 'oscuro' ? 'claro' : 'oscuro';
            aplicarTema(actual);
            localStorage.setItem('tema', actual);
        });
    }
});
