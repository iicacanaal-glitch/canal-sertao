document.addEventListener("DOMContentLoaded", function() {

    // Reservatório
    const usoReservatorio = document.getElementById("id_uso_reservatorio");
    const divVolReservatorio = document.getElementById("div_vol_reservatorio");

    // Uso coletivo
    const usoColetivo = document.getElementById("id_uso_coletivo");
    const divQuantColetivo = document.getElementById("div_quant_coletivo");

    function toggleReservatorio() {
        if (usoReservatorio && usoReservatorio.checked) {
            divVolReservatorio.style.display = "block";
        } else {
            divVolReservatorio.style.display = "none";
        }
    }

    function toggleColetivo() {
        if (usoColetivo && usoColetivo.checked) {
            divQuantColetivo.style.display = "block";
        } else {
            divQuantColetivo.style.display = "none";
        }
    }

    // Executar ao carregar
    toggleReservatorio();
    toggleColetivo();

    // Eventos
    if (usoReservatorio) {
        usoReservatorio.addEventListener("change", toggleReservatorio);
    }

    if (usoColetivo) {
        usoColetivo.addEventListener("change", toggleColetivo);
    }

});
