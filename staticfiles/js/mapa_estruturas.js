var map = L.map('map', {
    center: [-9.4, -37.2],
    zoom: 9
});


// =============================
// DADOS DOS TRECHOS
// =============================
const dadosTrechos = {
    "Trecho 1": { extensao: "45 km", percentual: "100%" },
    "Trecho 2": { extensao: "19,7 km", percentual: "100%" },
    "Trecho 3": { extensao: "28,23 km", percentual: "100%" },
    "Trecho 4": { extensao: "30,47 km", percentual: "100%" },
    "Trecho 5": { extensao: "26,60 km", percentual: "5,64%" },
    "Trecho restante": { extensao: "100 km", percentual: "0%" }
};


// =============================
// PANES
// =============================
map.createPane('municipiosPane');
map.getPane('municipiosPane').style.zIndex = 400;

map.createPane('trechosPane');
map.getPane('trechosPane').style.zIndex = 500;

map.createPane('estruturasPane');
map.getPane('estruturasPane').style.zIndex = 600;

map.createPane('pontosPane');
map.getPane('pontosPane').style.zIndex = 900;


// =============================
// BASEMAPS
// =============================
var satelite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: 'Tiles © Esri' }
).addTo(map);

var osm = L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    { attribution: '© OpenStreetMap' }
);


// =============================
// CONTROLE
// =============================
let controleAdicionado = false;


// =============================
// CORES DOS TRECHOS
// =============================
let contadorCor = 0;

function getCorTrecho() {
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


// =============================
// CANAL DO SERTÃO
// =============================
var listaTrechos = [];
var trechosOrdenados = {};

fetch(geojsonCanal)
.then(response => response.json())
.then(data => {

    data.features.forEach(function(feature) {

        let nome = feature.properties.Name || "Trecho";

        let corTrecho = getCorTrecho();

        let layer = L.geoJSON(feature, {
            pane: 'trechosPane',

            style: {
                color: corTrecho,
                weight: 4
            },

            onEachFeature: function(feature, camada) {

                camada.on({

                    mouseover: function(e) {
                        e.target.setStyle({
                            weight: 6
                        });

                        e.target.bindTooltip(nome, {
                            direction: "top",
                            className: "tooltip-trecho"
                        }).openTooltip();
                    },

                    mouseout: function(e) {
                        e.target.setStyle({
                            weight: 4
                        });

                        e.target.closeTooltip();
                    }
                });
            }
        });

        let info = dadosTrechos[nome];

        let popupContent = `<b>${nome}</b>`;

        if (info) {
            popupContent += `
                <br><strong>Extensão:</strong> ${info.extensao}
                <br><strong>Executado:</strong> ${info.percentual}
            `;
        }

        layer.bindPopup(popupContent);

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
// MUNICÍPIOS
// =============================
var camadaMunicipios;

fetch("/static/geojson/municipios.geojson")
.then(response => response.json())
.then(data => {

    camadaMunicipios = L.geoJSON(data, {
        pane: 'municipiosPane',

        interactive: false,

        style: {
            color: "#000",
            weight: 1.5,
            fillOpacity: 0
        },

        onEachFeature: function(feature, layer) {

            let nome = feature.properties.nome || "Município";

            layer.on({

                mouseover: function(e) {
                    e.target.setStyle({
                        weight: 3,
                        color: "#007bff"
                    });

                    e.target.bindTooltip(nome, {
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


// =============================
// ESTRUTURAS (POLÍGONOS)
// =============================
var camadaEstruturas;

fetch(geojsonEstruturas)
.then(response => response.json())
.then(data => {

    camadaEstruturas = L.geoJSON(data, {
        pane: 'estruturasPane',

        interactive: false,

        style: {
            color: '#ffbe0b',
            weight: 2,
            fillColor: '#ffbe0b',
            fillOpacity: 0.6
        }
    });

    camadaEstruturas.addTo(map);

    criarControle();
});


// =============================
// ESTRUTURAS PONTO
// =============================
var camadaPontos;

fetch(geojsonEstruturasPonto)
.then(response => response.json())
.then(data => {

    camadaPontos = L.geoJSON(data, {
        pane: 'pontosPane',

        pointToLayer: function(feature, latlng) {
            return L.circleMarker(latlng, {
                radius: 8,
                fillColor: '#d90429',
                color: '#fff',
                weight: 2,
                fillOpacity: 1
            });
        },

        onEachFeature: function(feature, layer) {

            let nome = feature.properties.Name || "Estrutura Pontual";

            layer.bindPopup(`<b>${nome}</b>`);
        }
    });

    camadaPontos.addTo(map);

    camadaPontos.bringToFront();

    criarControle();
});


// =============================
// CONTROLE DE CAMADAS
// =============================
function criarControle() {

    if (
        !camadaMunicipios ||
        !camadaEstruturas ||
        !camadaPontos ||
        Object.keys(trechosOrdenados).length === 0 ||
        controleAdicionado
    ) return;

    let baseMaps = {
        "🗺️ Mapa": osm,
        "🛰️ Satélite": satelite
    };

    let overlayMaps = {
        "📍 Municípios": camadaMunicipios,
        ...trechosOrdenados,
        "🏗️ Estruturas": camadaEstruturas,
        "📌 Estruturas Pontuais": camadaPontos
    };

    L.control.layers(baseMaps, overlayMaps, {
        collapsed: false
    }).addTo(map);

    controleAdicionado = true;
}
