var map = L.map('map', {
    center: [-9.4, -37.2],
    zoom: 9
});

// ===== PANES (controle de profundidade) =====
map.createPane('municipiosPane');
map.getPane('municipiosPane').style.zIndex = 400;

map.createPane('trechosPane');
map.getPane('trechosPane').style.zIndex = 500;


// ===== BASE MAP =====
var satelite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: 'Tiles © Esri' }
).addTo(map);

var osm = L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    { attribution: '© OpenStreetMap' }
);


// ===== CAMADAS DO CANAL =====
var listaCamadas = [];
var camadasOrdenadas = {};

fetch(geojsonUrl)
    .then(response => response.json())
    .then(data => {

        data.features.forEach(function(feature) {

            var nome = feature.properties.Name || "Trecho";

            var layer = L.geoJSON(feature, {
                pane: 'trechosPane', // 👈 sempre por cima
                style: {
                    color: getCor(),
                    weight: 4
                }
            });

            layer.bindPopup("<b>" + nome + "</b>");

            listaCamadas.push({
                nome: nome,
                layer: layer
            });

            layer.addTo(map);
        });

        // Ordenação alfabética
        listaCamadas.sort((a, b) =>
            a.nome.localeCompare(b.nome, 'pt-BR', { sensitivity: 'base' })
        );

        listaCamadas.forEach(item => {
            camadasOrdenadas["🚰 " + item.nome] = item.layer;
        });

        criarControle();
    });


// ===== MUNICÍPIOS (COM HOVER) =====
var camadaMunicipios;

fetch("/static/geojson/municipios.geojson")
    .then(response => response.json())
    .then(data => {

        camadaMunicipios = L.geoJSON(data, {
            pane: 'municipiosPane', // 👈 fica abaixo
            style: {
                color: "#000000",
                weight: 1.5,
                fillOpacity: 0
            },

            onEachFeature: function(feature, layer) {

                let nome = feature.properties.nome || "Município";

                layer.on({

                    mouseover: function(e) {
                        let layerAtual = e.target;

                        layerAtual.setStyle({
                            weight: 3,
                            color: "#007bff"
                        });

                        layerAtual.bindTooltip(nome, {
                            permanent: false,
                            direction: "center",
                            className: "tooltip-municipio"
                        }).openTooltip();
                    },

                    mouseout: function(e) {
                        camadaMunicipios.resetStyle(e.target);
                        e.target.closeTooltip();
                    }
                });
            }
        });

        camadaMunicipios.addTo(map);

        criarControle();
    });


// ===== CONTROLE DE CAMADAS =====
function criarControle() {

    if (!camadaMunicipios || Object.keys(camadasOrdenadas).length === 0) return;

    var baseMaps = {
        "🗺️ Mapa": osm,
        "🛰️ Satélite": satelite
    };

    var overlayMaps = {
        "📍 Municípios": camadaMunicipios,
        ...camadasOrdenadas
    };

    L.control.layers(baseMaps, overlayMaps, {
        collapsed: false
    }).addTo(map);
}


// ===== CORES =====
let contadorCor = 0;

function getCor() {
    const cores = [
        "#007bff",
        "#28a745",
        "#ffc107",
        "#dc3545",
        "#6f42c1",
        "#17a2b8"
    ];

    let cor = cores[contadorCor % cores.length];
    contadorCor++;
    return cor;
}
