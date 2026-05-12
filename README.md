# Sala de Situacao

Aplicacao Django para uma sala de situação com acompanhamento de projetos, irrigantes, paradas operacionais, documentos, ouvidoria e previsao do tempo.

## Principais modulos

- `Projetos`: cadastro, listagem, detalhamento e priorizacao por score.
- `Irrigantes`: registro de produtores e dados tecnicos de captacao.
- `Paradas`: controle de paradas programadas e emergenciais.
- `Documentos`: organizacao de arquivos por categoria.
- `Ouvidoria`: recebimento, consulta e tratamento de manifestacoes.
- `Previsao do tempo`: consulta por municipio com dados da OpenWeather.

## Tecnologias

- Python
- Django
- SQLite
- Plotly
- Requests

## Estrutura principal

- `core/`: models, forms, views, urls e testes da aplicacao.
- `templates/`: templates HTML organizados por modulo.
- `static/`: CSS, JavaScript, imagens e arquivos GeoJSON.
- `media/`: uploads em tempo de execucao.

## Desenvolvedor

Desenvolvido por Adelson da Silva Santos, Engenheiro Ambiental e Sanitarista.
Cargo: Analista Técnico Júnior da HIDROBR Consultoria  Ltda.


## Como rodar

Este projeto usa o ambiente Anaconda `sala_situacao`.

### 1. Ative o ambiente

Ative o ambiente virtual.

### 2. Instale as dependencias

Se ainda nao estiverem instaladas no ambiente:

```powershell
pip install django requests plotly pillow
```

### 3. Aplique migracoes

```powershell
python manage.py migrate
```

### 4. Inicie o servidor

```powershell
python manage.py runserver
```

O sistema ficara disponivel em [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Testes

Para executar os testes automatizados:

```powershell
python manage.py test core
```

Se preferir chamar direto pelo executavel do Anaconda:

```powershell
C:\Users\Usuario\anaconda3\Scripts\conda.exe run -n sala_situacao python manage.py test core
```

## Observacoes

- O projeto esta configurado com `AUTH_USER_MODEL = 'core.User'`.
- O banco SQLite local (`db.sqlite3`) nao deve ser versionado.
- Uploads e arquivos coletados de estaticos tambem nao devem ser versionados.
