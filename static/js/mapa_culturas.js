var map = L.map('map', {
    center: [-9.4, -37.2],
    zoom: 9
});

// =============================
// 🧱 PANES
// =============================
map.createPane('usoPane');
map.getPane('usoPane').style.zIndex = 400;

map.createPane('trechosPane');
map.getPane('trechosPane').style.zIndex = 500;


// =============================
// 🛰️ BASE MAP
// =============================
var satelite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: 'Tiles © Esri' }
).addTo(map);


// =============================
// 🎨 CORES FIXAS (15 classes)
// =============================
var coresUso = {
    "Afloramento Rochoso": "#8c8c8c",
    "Área Urbanizada": "#d62828",
    "Campo Alagado e Área Pantanosa": "#4cc9f0",
    "Cana": "#ffd60a",
    "Formação Campestre": "#90be6d",
    "Formação Florestal": "#2d6a4f",
    "Formação Savânica": "#a3b18a",
    "Mineração": "#6c757d",
    "Mosaico de Usos": "#f4a261",
    "Outras Áreas não Vegetadas": "#adb5bd",
    "Outras Lavouras Perenes": "#52b788",
    "Outras Lavouras Temporárias": "#80ed99",
    "Pastagem": "#b7e4c7",
    "Rio, Lago e Oceano": "#0077b6",
    "Silvicultura": "#40916c"
};


// =============================
// 🌱 CLASSES QUE INICIAM ATIVAS
// =============================
var classesAtivas = [
    "Outras Lavouras Perenes",
    "Outras Lavouras Temporárias",
    "Silvicultura"
];


// =============================
// 🌱 USO DO SOLO
// =============================
var listaUso = [];
var usoOrdenado = {};

fetch(geojsonUso)
    .then(res => res.json())
    .then(data => {

        data.features.forEach(function(feature) {

            var nome = feature.properties.Legenda || "Uso do Solo";

            var layer = L.geoJSON(feature, {
                pane: 'usoPane',

                style: {
                    color: "#333",
                    weight: 1,
                    fillColor: coresUso[nome] || "#ccc",
                    fillOpacity: 0.6
                },

                onEachFeature: function(feature, camada) {

                    let nome = feature.properties.Legenda;

                    camada.on({

                        mouseover: function(e) {
                            let l = e.target;

                            l.setStyle({
                                weight: 2,
                                color: "#000"
                            });

                            l.bindTooltip(nome, {
                                permanent: false,
                                direction: "center",
                                className: "tooltip-uso"
                            }).openTooltip();
                        },

                        mouseout: function(e) {
                            e.target.setStyle({
                                weight: 1,
                                color: "#333"
                            });
                            e.target.closeTooltip();
                        }
                    });
                }
            });

            layer.bindPopup("<b>" + nome + "</b>");

            listaUso.push({
                nome: nome,
                layer: layer
            });

            // 🔥 Só adiciona no mapa se estiver na lista ativa
            if (classesAtivas.includes(nome)) {
                layer.addTo(map);
            }
        });

        // 🔥 Ordenação alfabética
        listaUso.sort((a, b) =>
            a.nome.localeCompare(b.nome, 'pt-BR', { sensitivity: 'base' })
        );

        listaUso.forEach(item => {
            usoOrdenado["🌱 " + item.nome] = item.layer;
        });

        criarControle();
    });


// =============================
// 🚰 TRECHOS DO CANAL
// =============================
var listaTrechos = [];
var trechosOrdenados = {};

fetch(geojsonTrechos)
    .then(res => res.json())
    .then(data => {

        data.features.forEach(function(feature) {

            var nome = feature.properties.Name || "Trecho";

            var layer = L.geoJSON(feature, {
                pane: 'trechosPane',
                style: {
                    color: "#00ffff",
                    weight: 4
                }
            });

            layer.bindPopup("<b>" + nome + "</b>");

            listaTrechos.push({
                nome: nome,
                layer: layer
            });

            layer.addTo(map);
        });

        listaTrechos.sort((a, b) =>
            a.nome.localeCompare(b.nome, 'pt-BR', { sensitivity: 'base' })
        );

        listaTrechos.forEach(item => {
            trechosOrdenados["🚰 " + item.nome] = item.layer;
        });

        criarControle();
    });


// =============================
// 🎛️ CONTROLE DE CAMADAS
// =============================
function criarControle() {

    if (
        Object.keys(usoOrdenado).length === 0 ||
        Object.keys(trechosOrdenados).length === 0
    ) return;

    var overlayMaps = {
        ...usoOrdenado,
        ...trechosOrdenados
    };

    L.control.layers(null, overlayMaps, {
        collapsed: false
    }).addTo(map);
}
