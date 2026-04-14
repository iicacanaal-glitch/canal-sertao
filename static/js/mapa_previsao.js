var map = L.map('map').setView([-9.4, -37.5], 10);

// =============================
// 🧱 PANES (controle de ordem)
// =============================
map.createPane('municipiosPane');
map.getPane('municipiosPane').style.zIndex = 400;

map.createPane('canalPane');
map.getPane('canalPane').style.zIndex = 500;

// =============================
// 🗺️ BASE MAP
// =============================
var satelite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: 'Tiles © Esri' }
).addTo(map);


// =============================
// 🚰 TRECHOS DO CANAL
// =============================
var listaTrechos = [];
var trechosOrdenados = {};

fetch('/static/geojson/canal_trechos.geojson')
    .then(response => response.json())
    .then(data => {

        data.features.forEach(function(feature) {

            var nome = feature.properties.Name || "Trecho";

            var layer = L.geoJSON(feature, {
                pane: 'canalPane',
                style: {
                    color: getCor(),
                    weight: 4
                }
            });

            layer.bindPopup("<b>" + nome + "</b>");

            listaTrechos.push({
                nome: nome,
                layer: layer
            });
        });

        // 🔥 ordenar alfabeticamente
        listaTrechos.sort((a, b) =>
            a.nome.localeCompare(b.nome, 'pt-BR', { sensitivity: 'base' })
        );

        listaTrechos.forEach(item => {

            trechosOrdenados[item.nome] = item.layer;

            // 🔥 NÃO adiciona automaticamente "Trecho restante"
            if (item.nome.toLowerCase() !== "trecho restante") {
                item.layer.addTo(map);
            }
        });

        criarControle();
    });


// =============================
// 📍 MUNICÍPIOS (COM DADOS)
// =============================
var camadaMunicipios;

fetch('/static/geojson/municipios.geojson')
    .then(response => response.json())
    .then(data => {

        camadaMunicipios = L.geoJSON(data, {
            pane: 'municipiosPane',
            style: {
                color: "#000",
                weight: 1.5,
                fillOpacity: 0.1
            },

            onEachFeature: function(feature, layer) {

              let nome = feature.properties.nome || "";

              let dados = dados_municipios.find(m => m.nome === nome);

              let popup = "<b>" + nome + "</b><br>";

              if (dados) {
                  popup +=
                      "🌡️ Temp: " + Number(dados.temp).toFixed(1) + " °C<br>" +
                      "☁️ " + dados.descricao;
              } else {
                  popup += "Sem dados";
              }

              layer.bindPopup(popup);

              layer.on({

                  mouseover: function(e) {
                      let l = e.target;

                      l.setStyle({
                          weight: 3,
                          color: "#007bff",
                          fillOpacity: 0.25
                      });

                      if (dados) {
                          l.bindTooltip(
                              `
                              <strong>${nome}</strong><br>
                              🌡️ ${Number(dados.temp).toFixed(1)} °C<br>
                              ☁️ ${dados.descricao}
                              `,
                              {
                                  direction: "top",
                                  sticky: true,
                                  className: "tooltip-municipio"
                              }
                          ).openTooltip();
                      }
                  },

                  mouseout: function(e) {
                      camadaMunicipios.resetStyle(e.target);
                      e.target.closeTooltip();
                  },

                  click: function() {
                      if (dados) {
                          window.location.href = `/previsao-tempo/?municipio=${dados.id}`;
                      }
                  }
              });
          }

        });

        camadaMunicipios.addTo(map);

        criarControle();
    });


// =============================
// 🎛️ CONTROLE DE CAMADAS
// =============================
function criarControle() {

    if (!camadaMunicipios || Object.keys(trechosOrdenados).length === 0) return;

    var overlayMaps = {
        "📍 Municípios": camadaMunicipios,
        ...trechosOrdenados
    };

    L.control.layers(null, overlayMaps, {
        collapsed: false
    }).addTo(map);
}


// =============================
// 🎨 CORES DOS TRECHOS
// =============================
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
