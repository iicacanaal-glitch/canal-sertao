import requests
import plotly.graph_objs as go
import plotly.offline as opy

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Parada, Irrigantes, Municipio, Documento, CategoriaDocumento, Projeto, Manifestacao, ManifestacaoHistorico
from .forms import LoginForm, ParadaForm, IrrigantesForm, DocumentoForm, CategoriaDocumentoForm, ProjetoForm, ManifestacaoForm

from datetime import datetime, timedelta
from collections import defaultdict


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'


@login_required
def home(request):

    manifestacoes = Manifestacao.objects.all()
    paradas = Parada.objects.order_by('-data_inicio')[:5]

    context = {
        'total_projetos': Projeto.objects.count(),
        'total_manifestacoes': manifestacoes.count(),
        'em_andamento': manifestacoes.filter(status='em_andamento').count(),
        'recebido': manifestacoes.filter(status='recebido').count(),
        'manifestacoes_recentes': manifestacoes[:5],
        'paradas_recentes': paradas,
    }

    return render(request, 'home.html', context)


@login_required
def lista_paradas(request):
    paradas = Parada.objects.all().order_by('-data_inicio')
    return render(request, 'paradas/lista_paradas.html', {
        'paradas': paradas
    })


@login_required
def nova_parada(request):
    if request.method == 'POST':
        form = ParadaForm(request.POST)
        if form.is_valid():
            parada = form.save(commit=False)
            parada.cadastrante = request.user
            parada.save()
            form.save_m2m()
            return redirect('lista_paradas')
    else:
        form = ParadaForm()

    return render(request, 'paradas/nova_parada.html', {
        'form': form
    })


@login_required
def lista_irrigantes(request):
    irrigantes = Irrigantes.objects.all().order_by('nome')
    return render(request, 'irrigantes/lista_irrigantes.html', {
        'irrigantes': irrigantes
    })


@login_required
def novo_irrigante(request):
    if request.method == 'POST':
        form = IrrigantesForm(request.POST, request.FILES)
        if form.is_valid():
            irrigante = form.save(commit=False)
            irrigante.cadastrante = request.user
            irrigante.save()
            return redirect('lista_irrigantes')
    else:
        form = IrrigantesForm()

    return render(request, 'irrigantes/novo_irrigante.html', {
        'form': form
    })


@login_required
def previsao_tempo(request):
    municipios = Municipio.objects.filter(ativo=True)

    municipio_id = request.GET.get('municipio')
    previsao_hoje = []
    dados_mapa = []

    api_key = "40fd160bb348bf3397a70f115255ea07"

    # ===== DADOS DO MAPA =====
    for m in municipios:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={m.latitude}&lon={m.longitude}&appid={api_key}&units=metric&lang=pt_br"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                dados_mapa.append({
                    'nome': m.nome,
                    'lat': m.latitude,
                    'lon': m.longitude,
                    'temp': data['main']['temp'],
                    'descricao': data['weather'][0]['description'],
                    'icone': data['weather'][0]['icon'],
                })
        except:
            pass

    # ===== VARIÁVEIS DOS GRÁFICOS =====
    grafico_temp = None
    grafico_chuva = None
    grafico_acumulado = None

    previsao_cards = []

    # ===== PREVISÃO MUNICÍPIO SELECIONADO =====
    if municipio_id:
        municipio = Municipio.objects.get(id=municipio_id)

        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={municipio.latitude}&lon={municipio.longitude}&appid={api_key}&units=metric&lang=pt_br"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            previsao_5dias = defaultdict(list)

            for item in data['list']:
                data_hora = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")
                data_dia = data_hora.date()

                temp = item['main']['temp']
                prob_chuva = item.get('pop', 0) * 100
                icone = item['weather'][0]['icon']
                descricao = item['weather'][0]['description']

                previsao_5dias[data_dia].append({
                    'temp': temp,
                    'chuva': prob_chuva,
                    'icone': icone,
                    'descricao': descricao
                })

            dias_semana = {
                'Mon': 'Seg',
                'Tue': 'Ter',
                'Wed': 'Qua',
                'Thu': 'Qui',
                'Fri': 'Sex',
                'Sat': 'Sáb',
                'Sun': 'Dom',
            }

            for dia, valores in previsao_5dias.items():
                temps = [v['temp'] for v in valores]
                chuvas = [v['chuva'] for v in valores]

                dia_semana_en = dia.strftime("%a")
                dia_semana_pt = dias_semana[dia_semana_en]

                previsao_cards.append({
                    'data': dia.strftime("%d/%m"),
                    'dia_semana': dia_semana_pt,
                    'temp_min': min(temps),
                    'temp_max': max(temps),
                    'chuva': max(chuvas),
                    'icone': valores[0]['icone'],
                    'descricao': valores[0]['descricao'],
                })

            hoje = datetime.now().date()

            horas = []
            temperaturas = []
            chuva = []
            chuva_acumulada = []

            acumulado = 0

            for item in data['list']:
                data_hora = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")

                if data_hora.date() == hoje:
                    hora = data_hora.strftime("%H:%M")
                    temp = item['main']['temp']
                    prob_chuva = item.get('pop', 0) * 100
                    descricao = item['weather'][0]['description']
                    icone = item['weather'][0]['icon']
                    chuva_mm = item.get('rain', {}).get('3h', 0)

                    acumulado += chuva_mm

                    horas.append(hora)
                    temperaturas.append(temp)
                    chuva.append(prob_chuva)
                    chuva_acumulada.append(acumulado)

                    previsao_hoje.append({
                        'hora': hora,
                        'temp': temp,
                        'chuva': prob_chuva,
                        'descricao': descricao,
                        'icone': icone,
                        'chuva_mm': chuva_mm,
                    })


            # ===== GRÁFICO TEMPERATURA =====
            fig_temp = go.Figure()

            fig_temp.add_trace(go.Scatter(
                x=horas,
                y=temperaturas,
                mode='lines+markers',
                name='Temperatura',
                line=dict(width=3)
            ))

            fig_temp.update_layout(
                title='Temperatura Hora a Hora',
                xaxis_title='Hora',
                yaxis_title='Temperatura (°C)',
                template='plotly_white',
                height=350
            )

            grafico_temp = opy.plot(fig_temp, auto_open=False, output_type='div')

            # ===== GRÁFICO CHUVA =====
            fig_chuva = go.Figure()

            fig_chuva.add_trace(go.Bar(
                x=horas,
                y=chuva,
                name='Probabilidade de Chuva'
            ))

            fig_chuva.update_layout(
                title='Probabilidade de Chuva (%)',
                xaxis_title='Hora',
                yaxis_title='%',
                template='plotly_white',
                height=350
            )

            grafico_chuva = opy.plot(fig_chuva, auto_open=False, output_type='div')

            # ===== GRÁFICO CHUVA ACUMULADA =====
            fig_acum = go.Figure()

            fig_acum.add_trace(go.Scatter(
                x=horas,
                y=chuva_acumulada,
                mode='lines+markers',
                name='Chuva acumulada',
                line=dict(width=3, color='blue'),
                fill='tozeroy'
            ))

            fig_acum.update_layout(
                title='Chuva Acumulada (mm)',
                xaxis_title='Hora',
                yaxis_title='mm',
                template='plotly_white',
                height=350
            )

            grafico_acumulado = opy.plot(fig_acum, auto_open=False, output_type='div')


    context = {
        'municipios': municipios,
        'previsao_hoje': previsao_hoje,
        'dados_mapa': dados_mapa,
        'municipio_id': municipio_id,
        'grafico_temp': grafico_temp,
        'grafico_chuva': grafico_chuva,
        'grafico_acumulado': grafico_acumulado,
        'previsao_cards': previsao_cards,
        'previsao_cards': previsao_cards,
    }

    return render(request, 'clima/previsao_tempo.html', context)


@login_required
def lista_documentos(request):
    busca = request.GET.get('busca')
    categoria_id = request.GET.get('categoria')

    documentos = Documento.objects.all().order_by('-data_upload')
    categorias = CategoriaDocumento.objects.filter(pai__isnull=True)

    # 🔎 Filtro por busca
    if busca:
        documentos = documentos.filter(
            Q(titulo__icontains=busca) |
            Q(descricao__icontains=busca)
        )

    # 📁 Filtro por categoria
    categoria_selecionada = None
    if categoria_id:
        categoria_selecionada = get_object_or_404(CategoriaDocumento, id=categoria_id)
        documentos = documentos.filter(categoria=categoria_selecionada)

    context = {
        'documentos': documentos,
        'categorias': categorias,
        'categoria_selecionada': categoria_selecionada,
        'busca': busca,
    }

    return render(request, 'documentos/lista_documentos.html', context)


@login_required
def novo_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.cadastrante = request.user
            documento.save()
            return redirect('lista_documentos')
    else:
        form = DocumentoForm()

    return render(request, 'documentos/novo_documento.html', {'form': form})


@login_required
def detalhe_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    return render(request, 'documentos/detalhe_documento.html', {
        'documento': documento
    })


@login_required
def editar_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            form.save()
            return redirect('lista_documentos')
    else:
        form = DocumentoForm(instance=documento)

    return render(request, 'documentos/novo_documento.html', {
        'form': form,
        'editar': True
    })


@login_required
def excluir_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    if request.method == 'POST':
        documento.delete()
        return redirect('lista_documentos')

    return render(request, 'documentos/confirmar_exclusao.html', {
        'objeto': documento
    })


@login_required
def nova_categoria(request):
    if request.method == 'POST':
        form = CategoriaDocumentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_documentos')
    else:
        form = CategoriaDocumentoForm()

    return render(request, 'documentos/nova_categoria.html', {'form': form})


@login_required
def documentos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(CategoriaDocumento, id=categoria_id)

    subcategorias = categoria.subcategorias.all()
    documentos = Documento.objects.filter(categoria=categoria)

    context = {
        'categoria': categoria,
        'subcategorias': subcategorias,
        'documentos': documentos,
    }

    return render(request, 'documentos/explorador.html', context)


@login_required
def mapa_canal(request):
    return render(request, 'mapa/mapa_canal.html')


@login_required
def mapa_solos(request):
    return render(request, 'mapa/mapa_solos.html')


@login_required
def mapa_culturas(request):
    return render(request, 'mapa/mapa_culturas.html')


@login_required
def lista_projetos(request):
    projetos = Projeto.objects.all()

    return render(request, 'projetos/lista.html', {
        'projetos': projetos
    })


@login_required
def cadastrar_projeto(request):
    if request.user.grupo != 'segov':
        messages.error(request, "Você não tem permissão para cadastrar Projetos!")
        return redirect('home')
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            projeto = form.save(commit=False)
            projeto.cadastrante = request.user
            projeto.save()
            return redirect('lista_projetos')
    else:
        form = ProjetoForm()

    return render(request, 'projetos/form.html', {
        'form': form
    })


@login_required
def editar_projeto(request, projeto_id):
    if request.user.grupo != 'segov':
        messages.error(request, "Você não tem permissão para cadastrar Projetos!")
        return redirect('home')
    projeto = get_object_or_404(Projeto, id=projeto_id)

    if request.method == 'POST':
        form = ProjetoForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            return redirect('lista_projetos')
    else:
        form = ProjetoForm(instance=projeto)

    return render(request, 'projetos/form.html', {
        'form': form,
        'editar': True
    })


@login_required
def excluir_projeto(request, projeto_id):
    projeto = get_object_or_404(Projeto, id=projeto_id)

    if request.method == 'POST':
        projeto.delete()
        return redirect('lista_projetos')

    return render(request, 'projetos/confirmar_exclusao.html', {
        'objeto': projeto
    })


def escolher_classificacao(request):
    if request.method == 'POST':
        classificacao = request.POST.get('classificacao')

        request.session['classificacao'] = classificacao

        return redirect('enviar_manifestacao')

    return render(request, 'ouvidoria/classificacao.html')


def enviar_manifestacao(request):
    classificacao = request.session.get('classificacao')

    if not classificacao:
        return redirect('escolher_classificacao')

    if request.method == 'POST':
        form = ManifestacaoForm(request.POST, request.FILES)

        if form.is_valid():
            manifestacao = form.save(commit=False)

            manifestacao.classificacao = classificacao

            if form.cleaned_data.get('anonimo'):
                manifestacao.nome = "Anônimo"
                manifestacao.email = None

            if classificacao == 'agropecuaria':
                manifestacao.setor_responsavel = 'SEAGRI'
            elif classificacao == 'consumo_humano':
                manifestacao.setor_responsavel = 'CASAL'
            else:
                manifestacao.setor_responsavel = 'CASAL'

            manifestacao.save()

            ManifestacaoHistorico.objects.create(
                manifestacao=manifestacao,
                status='recebido',
                descricao='Manifestação registrada no sistema'
            )

            if 'classificacao' in request.session:
                del request.session['classificacao']

            messages.success(
                request,
                f"Manifestação enviada com sucesso! Protocolo: {manifestacao.protocolo}"
            )

            return redirect('acompanhar_manifestacao', protocolo=manifestacao.protocolo)

        else:
            messages.error(request, "Corrija os erros abaixo.")

    else:
        form = ManifestacaoForm()

    return render(request, 'ouvidoria/form.html', {
        'form': form,
        'classificacao': classificacao
    })


def consulta_manifestacao(request):
    if request.method == 'POST':
        protocolo = request.POST.get('protocolo')

        try:
            manifestacao = Manifestacao.objects.get(protocolo=protocolo)
            return redirect('acompanhar_manifestacao', protocolo=protocolo)
        except Manifestacao.DoesNotExist:
            messages.error(request, "Protocolo não encontrado.")

    return render(request, 'ouvidoria/consulta.html')


def acompanhar_manifestacao(request, protocolo):
    manifestacao = get_object_or_404(Manifestacao, protocolo=protocolo)

    historico = manifestacao.historico.all().order_by('data')

    return render(request, 'ouvidoria/detalhe.html', {
        'manifestacao': manifestacao,
        'historico': historico
    })


@login_required
def lista_manifestacoes(request):
    user = request.user

    limite = timezone.now() - timedelta(days=7)

    if user.grupo == 'seagri':
        manifestacoes = Manifestacao.objects.filter(setor_responsavel='SEAGRI')

    elif user.grupo == 'casal':
        manifestacoes = Manifestacao.objects.filter(setor_responsavel='CASAL')

    else:
        messages.error(request, "Você não tem permissão para acessar a ouvidoria!")
        return redirect('home')

    manifestacoes = manifestacoes.exclude(
        status='concluido',
        ultima_atualizacao__lt=limite
    )

    return render(request, 'ouvidoria/lista.html', {
        'manifestacoes': manifestacoes
    })


@login_required
def atualizar_status(request, pk):
    manifestacao = get_object_or_404(Manifestacao, pk=pk)

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        descricao = request.POST.get('descricao')

        # atualiza status
        manifestacao.status = novo_status
        manifestacao.save()

        # salva histórico
        ManifestacaoHistorico.objects.create(
            manifestacao=manifestacao,
            status=novo_status,
            descricao=descricao,
            usuario=request.user if request.user.is_authenticated else None
        )

        messages.success(request, "Status atualizado com sucesso.")

        return redirect('lista_manifestacoes')

    return render(request, 'ouvidoria/atualizar_status.html', {
        'manifestacao': manifestacao,
        'status_choices': Manifestacao.STATUS_CHOICES
    })
