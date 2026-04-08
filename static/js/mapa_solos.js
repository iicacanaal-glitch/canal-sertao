var map = L.map('map', {
    center: [-9.4, -37.2],
    zoom: 9
});

// =============================
// 🧱 PANES (ordem das camadas)
// =============================
map.createPane('solosPane');
map.getPane('solosPane').style.zIndex = 400;

map.createPane('trechosPane');
map.getPane('trechosPane').style.zIndex = 500;


// =============================
// 🛰️ BASE MAP (SATÉLITE)
// =============================
var satelite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: 'Tiles © Esri' }
).addTo(map);


// =============================
// 🎨 CORES FIXAS DOS SOLOS
// =============================
var coresFixas = [
    "#f4a261",
    "#e76f51",
    "#2a9d8f",
    "#8ab17d",
    "#264653",
    "#e9c46a",
    "#6a4c93",
    "#00b4d8"
];

var mapaCores = {};
var indiceCor = 0;

function getCorSolo(nome) {
    if (mapaCores[nome]) return mapaCores[nome];

    let cor = coresFixas[indiceCor % coresFixas.length];
    mapaCores[nome] = cor;
    indiceCor++;

    return cor;
}


// =============================
// 🌱 SOLOS
// =============================
var listaSolos = [];
var solosOrdenados = {};

fetch(geojsonSolos)
    .then(res => res.json())
    .then(data => {

        data.features.forEach(function(feature) {

            var nome = feature.properties.COMP1 || "Solo";

            var layer = L.geoJSON(feature, {
                pane: 'solosPane',

                style: {
                    color: "#333",
                    weight: 1,
                    fillColor: getCorSolo(nome),
                    fillOpacity: 0.6
                },

                onEachFeature: function(feature, camada) {

                    let nome = feature.properties.COMP1 || "Solo";

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
                                className: "tooltip-solo"
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

            listaSolos.push({
                nome: nome,
                layer: layer
            });

            layer.addTo(map);
        });

        // 🔥 Ordenação alfabética
        listaSolos.sort((a, b) =>
            a.nome.localeCompare(b.nome, 'pt-BR', { sensitivity: 'base' })
        );

        listaSolos.forEach(item => {
            solosOrdenados["🌱 " + item.nome] = item.layer;
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
        Object.keys(solosOrdenados).length === 0 ||
        Object.keys(trechosOrdenados).length === 0
    ) return;

    var overlayMaps = {
        ...solosOrdenados,   // 🔥 cada solo individual
        ...trechosOrdenados  // 🔥 cada trecho individual
    };

    L.control.layers(null, overlayMaps, {
        collapsed: false
    }).addTo(map);
}
