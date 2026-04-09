document.addEventListener('DOMContentLoaded', function () {

    console.log("form.js carregado ✅");

    const form = document.querySelector('form');
    if (!form) return;

    const selects = form.querySelectorAll('select');

    // =============================
    // 🎨 COR POR NOTA
    // =============================
    function aplicarCor(select) {
        const valor = parseInt(select.value);

        select.classList.remove('nota-baixa', 'nota-media', 'nota-alta');

        if (!valor) return;

        if (valor <= 2) {
            select.classList.add('nota-baixa');
        } else if (valor === 3) {
            select.classList.add('nota-media');
        } else {
            select.classList.add('nota-alta');
        }
    }

    // =============================
    // 🧠 CAPTURA DE VALORES
    // =============================
    function v(id) {
        const el = document.getElementById('id_' + id);
        return el && el.value ? parseInt(el.value) : 0;
    }


    // =============================
    // 🔢 CÁLCULO DO RESULTADO
    // =============================
    function calcularResultado() {

        const resultado =
            v('determinacao_legal') * 8 +
            v('impacto_metas') * 7 +
            v('alinhamento') * 7 +
            v('situacao') * 5 +
            v('dispo_recurso') * 8 +
            v('complexidade') * -2 +
            v('custo') * -3 +
            v('prazo') * -1 +
            v('riscos') * -4 +
            v('tempo_resultado') * -2;

        console.log({
            determinacao_legal: v('determinacao_legal'),
            impacto_metas: v('impacto_metas'),
            alinhamento: v('alinhamento')
        });

        mostrarResultado(resultado);
    }

    // =============================
    // 📊 MOSTRAR RESULTADO
    // =============================
    function mostrarResultado(valor) {

        const box = document.getElementById('resultado-box');
        const span = document.getElementById('resultado-valor');

        if (!box || !span) {
            console.warn("Box de resultado não encontrado ⚠️");
            return;
        }

        span.textContent = valor;

        box.style.display = 'block';

        // limpa cores
        box.classList.remove(
            'alert-info',
            'alert-success',
            'alert-warning',
            'alert-danger'
        );

        // aplica cor baseada no score
        if (valor >= 80) {
            box.classList.add('alert-success');
        } else if (valor >= 50) {
            box.classList.add('alert-warning');
        } else {
            box.classList.add('alert-danger');
        }
    }

    // =============================
    // 🎯 EVENTOS (FORMA ROBUSTA)
    // =============================
    document.addEventListener('change', function (e) {

        if (e.target.tagName === 'SELECT') {

            aplicarCor(e.target);
            calcularResultado();

        }

    });


    // =============================
    // 🚀 CALCULAR AO CARREGAR (caso edição)
    // =============================
    calcularResultado();

    // =============================
    // ✅ VALIDAÇÃO NO SUBMIT
    // =============================
    form.addEventListener('submit', function (e) {

        let valido = true;

        const obrigatorios = [
            'determinacao_legal',
            'impacto_metas',
            'alinhamento',
            'situacao',
            'dispo_recurso'
        ];

        obrigatorios.forEach(nome => {
            const campo = document.querySelector(`[name="${nome}"]`);

            if (!campo.value) {
                campo.classList.add('is-invalid');
                valido = false;
            } else {
                campo.classList.remove('is-invalid');
            }
        });

        if (!valido) {
            e.preventDefault();
            alert("Preencha os campos obrigatórios.");
        }

    });

});
