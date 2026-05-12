from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .context_processors import contador_ouvidoria
from .forms import DocumentoForm, IrrigantesForm, ManifestacaoForm
from .models import CategoriaDocumento, Documento, Manifestacao, ManifestacaoHistorico, Municipio, Projeto, User


class BaseDataMixin:
    def create_project(self, owner):
        return Projeto.objects.create(
            nome='Projeto Teste',
            descricao='Descricao',
            determinacao_legal=5,
            impacto_metas=4,
            alinhamento=4,
            situacao=3,
            dispo_recurso=3,
            complexidade=2,
            custo=2,
            prazo=2,
            riscos=2,
            tempo_resultado=2,
            cadastrante=owner,
        )

    def irrigante_form_data(self, municipio_id):
        return {
            'nome': 'Irrigante Teste',
            'apelido': '',
            'cpf': '123.456.789-00',
            'rg': '1234567',
            'estado_civil': 'Solteiro',
            'nome_mae': 'Maria',
            'data_nascimento': '1990-01-01',
            'conjuge': '',
            'cpf_conjuge': '',
            'rg_conjuge': '',
            'estado_civil_conjuge': '',
            'telefone': '82999999999',
            'municipio': municipio_id,
            'finalidade': 'Irrigacao',
            'latitude': '-10.123456',
            'longitude': '-36.123456',
            'nome_imovel': 'Sitio Teste',
            'comunidade': 'Comunidade',
            'area_total': '10.00',
            'area_irrigada': '5.00',
            'forma_ocupacao': 'Proprio',
            'permissao_de_uso': '',
            'num_permissao': '',
            'uso_individual': '',
            'uso_coletivo': '',
            'quant_coletivo': '',
            'num_lacre': '',
            'trecho_captacao': '',
            'vazao_requerida': '1.50',
            'potencia_bomba': '2.00',
            'dias_uso_por_semana': '5',
            'horas_uso_por_dia': '4',
            'diametro_succao': '2.50',
            'diametro_recalque': '2.00',
            'energia_utilizada': 'Eletrica',
            'vazao_bombeamento': '1.20',
            'distancia_captacao_destinacao': '50.00',
            'destinacao_apos_captacao': 'Lavoura',
            'uso_direto': 'on',
            'uso_reservatorio': '',
            'vol_reservatorio': '',
            'altura_recalque': '10.00',
        }


class ProjetoPermissionTests(TestCase, BaseDataMixin):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            password='test123',
            grupo='segov',
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='test123',
            grupo='segov',
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='test123',
            email='admin@example.com',
        )
        self.projeto = self.create_project(self.owner)

    def test_cadastrante_can_access_edit_page(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('editar_projeto', args=[self.projeto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projetos/form.html')

    def test_other_user_is_redirected_from_edit_page(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('editar_projeto', args=[self.projeto.id]))
        self.assertRedirects(response, reverse('home'))

    def test_superuser_can_access_edit_page(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('editar_projeto', args=[self.projeto.id]))
        self.assertEqual(response.status_code, 200)


class ProjetoAndCadastroPermissionTests(TestCase):
    def setUp(self):
        self.casal_user = User.objects.create_user(
            username='casal',
            password='test123',
            grupo='casal',
        )
        self.seg_user = User.objects.create_user(
            username='seg',
            password='test123',
            grupo='segov',
        )

    def test_non_segov_user_cannot_access_project_creation(self):
        self.client.force_login(self.casal_user)
        response = self.client.get(reverse('cadastrar_projeto'))
        self.assertRedirects(response, reverse('home'))

    def test_segov_user_can_access_project_creation(self):
        self.client.force_login(self.seg_user)
        response = self.client.get(reverse('cadastrar_projeto'))
        self.assertEqual(response.status_code, 200)


class ManifestacaoPermissionTests(TestCase):
    def setUp(self):
        self.seagri_user = User.objects.create_user(
            username='seagri_user',
            password='test123',
            grupo='seagri',
        )
        self.casal_user = User.objects.create_user(
            username='casal_user',
            password='test123',
            grupo='casal',
        )
        self.manifestacao_casal = Manifestacao.objects.create(
            tipo='reclamacao',
            assunto='Assunto',
            descricao='Descricao',
            classificacao='consumo_humano',
            setor_responsavel='CASAL',
            protocolo='PROTO001',
            status='recebido',
        )

    def test_user_cannot_update_manifestacao_from_other_sector(self):
        self.client.force_login(self.seagri_user)
        response = self.client.post(
            reverse('atualizar_status', args=[self.manifestacao_casal.id]),
            {'status': 'em_analise', 'descricao': 'Tentativa indevida'}
        )

        self.assertRedirects(response, reverse('lista_manifestacoes'))
        self.manifestacao_casal.refresh_from_db()
        self.assertEqual(self.manifestacao_casal.status, 'recebido')
        self.assertFalse(
            ManifestacaoHistorico.objects.filter(
                manifestacao=self.manifestacao_casal,
                status='em_analise',
            ).exists()
        )

        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any('permiss' in message.lower() for message in messages))

    def test_user_can_update_manifestacao_from_own_sector(self):
        self.client.force_login(self.casal_user)
        response = self.client.post(
            reverse('atualizar_status', args=[self.manifestacao_casal.id]),
            {'status': 'em_analise', 'descricao': 'Analise iniciada'}
        )

        self.assertRedirects(response, reverse('lista_manifestacoes'))
        self.manifestacao_casal.refresh_from_db()
        self.assertEqual(self.manifestacao_casal.status, 'em_analise')
        historico = ManifestacaoHistorico.objects.filter(manifestacao=self.manifestacao_casal)
        self.assertEqual(historico.count(), 1)
        self.assertEqual(historico.first().usuario, self.casal_user)


class ManifestacaoSubmissionTests(TestCase):
    def setUp(self):
        session = self.client.session
        session['classificacao'] = 'agropecuaria'
        session.save()

    def test_enviar_manifestacao_anonima_define_campos_automaticamente(self):
        response = self.client.post(
            reverse('enviar_manifestacao'),
            {
                'nome': '',
                'email': 'anon@example.com',
                'telefone': '82999999999',
                'anonimo': 'on',
                'tipo': 'denuncia',
                'assunto': 'Assunto anonimo',
                'descricao': 'Descricao',
                'municipio': 'Penedo',
            }
        )

        manifestacao = Manifestacao.objects.get(assunto='Assunto anonimo')
        self.assertRedirects(response, reverse('acompanhar_manifestacao', args=[manifestacao.protocolo]))
        self.assertEqual(manifestacao.nome, 'Anônimo')
        self.assertIsNone(manifestacao.email)
        self.assertEqual(manifestacao.setor_responsavel, 'SEAGRI')
        self.assertTrue(manifestacao.protocolo)
        self.assertTrue(
            ManifestacaoHistorico.objects.filter(
                manifestacao=manifestacao,
                status='recebido',
            ).exists()
        )

    def test_enviar_manifestacao_nao_anonima_define_setor_por_classificacao(self):
        session = self.client.session
        session['classificacao'] = 'consumo_humano'
        session.save()

        response = self.client.post(
            reverse('enviar_manifestacao'),
            {
                'nome': 'Joao',
                'email': 'joao@example.com',
                'telefone': '82999999999',
                'tipo': 'solicitacao',
                'assunto': 'Assunto nominal',
                'descricao': 'Descricao',
                'municipio': 'Penedo',
            }
        )

        manifestacao = Manifestacao.objects.get(assunto='Assunto nominal')
        self.assertRedirects(response, reverse('acompanhar_manifestacao', args=[manifestacao.protocolo]))
        self.assertEqual(manifestacao.nome, 'Joao')
        self.assertEqual(manifestacao.email, 'joao@example.com')
        self.assertEqual(manifestacao.setor_responsavel, 'CASAL')


class FormValidationTests(TestCase, BaseDataMixin):
    def setUp(self):
        self.municipio = Municipio.objects.create(
            nome='Penedo',
            ativo=True,
            latitude=-10.29,
            longitude=-36.58,
        )

    def test_irrigantes_form_requires_reservoir_volume_when_selected(self):
        data = self.irrigante_form_data(self.municipio.id)
        data['uso_reservatorio'] = 'on'
        form = IrrigantesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('vol_reservatorio', form.errors)

    def test_irrigantes_form_requires_collective_quantity_when_selected(self):
        data = self.irrigante_form_data(self.municipio.id)
        data['uso_coletivo'] = 'on'
        form = IrrigantesForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('quant_coletivo', form.errors)

    def test_manifestacao_form_requires_name_when_not_anonymous(self):
        form = ManifestacaoForm(data={
            'nome': '',
            'email': 'teste@example.com',
            'telefone': '82999999999',
            'tipo': 'denuncia',
            'assunto': 'Assunto',
            'descricao': 'Descricao',
            'municipio': 'Penedo',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)

    def test_manifestacao_form_rejects_invalid_file_extension(self):
        invalid_file = SimpleUploadedFile('arquivo.pdf', b'conteudo', content_type='application/pdf')
        form = ManifestacaoForm(
            data={
                'nome': 'Joao',
                'email': 'teste@example.com',
                'telefone': '82999999999',
                'tipo': 'denuncia',
                'assunto': 'Assunto',
                'descricao': 'Descricao',
                'municipio': 'Penedo',
            },
            files={'anexo': invalid_file}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('anexo', form.errors)

    def test_manifestacao_form_rejects_file_above_size_limit(self):
        big_file = SimpleUploadedFile('imagem.jpg', b'a' * (10 * 1024 * 1024 + 1), content_type='image/jpeg')
        form = ManifestacaoForm(
            data={
                'nome': 'Joao',
                'email': 'teste@example.com',
                'telefone': '82999999999',
                'tipo': 'denuncia',
                'assunto': 'Assunto',
                'descricao': 'Descricao',
                'municipio': 'Penedo',
            },
            files={'anexo': big_file}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('anexo', form.errors)

    def test_documento_form_rejects_file_above_size_limit(self):
        categoria = CategoriaDocumento.objects.create(nome='Tecnicos')
        big_file = SimpleUploadedFile('arquivo.pdf', b'a' * (50 * 1024 * 1024 + 1), content_type='application/pdf')
        form = DocumentoForm(
            data={
                'titulo': 'Documento grande',
                'descricao': 'Descricao',
                'categoria': categoria.id,
            },
            files={'arquivo': big_file}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('arquivo', form.errors)

    def test_documento_form_accepts_valid_file(self):
        categoria = CategoriaDocumento.objects.create(nome='Tecnicos')
        file_ok = SimpleUploadedFile('arquivo.pdf', b'conteudo', content_type='application/pdf')
        form = DocumentoForm(
            data={
                'titulo': 'Documento valido',
                'descricao': 'Descricao',
                'categoria': categoria.id,
            },
            files={'arquivo': file_ok}
        )
        self.assertTrue(form.is_valid())


class PrevisaoTempoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tempo_user',
            password='test123',
            grupo='casal',
        )
        self.municipio = Municipio.objects.create(
            nome='Penedo',
            ativo=True,
            latitude=-10.29,
            longitude=-36.58,
        )

    @staticmethod
    def _weather_payload():
        return {
            'main': {'temp': 27},
            'weather': [{'description': 'ensolarado', 'icon': '01d'}],
        }

    @staticmethod
    def _forecast_payload(base_date):
        day_with_data = base_date + timedelta(days=1)
        return {
            'list': [
                {
                    'dt_txt': f'{day_with_data:%Y-%m-%d} 09:00:00',
                    'main': {'temp': 26},
                    'weather': [{'description': 'nublado', 'icon': '02d'}],
                    'pop': 0.2,
                    'rain': {'3h': 0},
                },
                {
                    'dt_txt': f'{day_with_data:%Y-%m-%d} 12:00:00',
                    'main': {'temp': 29},
                    'weather': [{'description': 'aberto', 'icon': '03d'}],
                    'pop': 0.1,
                    'rain': {'3h': 0},
                },
            ]
        }

    @staticmethod
    def _forecast_payload_partial_today(base_date):
        next_day = base_date + timedelta(days=1)
        payload = {
            'list': [
                {
                    'dt_txt': f'{base_date:%Y-%m-%d} 18:00:00',
                    'main': {'temp': 28},
                    'weather': [{'description': 'fim de tarde', 'icon': '03d'}],
                    'pop': 0.1,
                    'rain': {'3h': 0},
                },
            ]
        }

        for hour in range(0, 24, 3):
            payload['list'].append({
                'dt_txt': f'{next_day:%Y-%m-%d} {hour:02d}:00:00',
                'main': {'temp': 24 + (hour / 10)},
                'weather': [{'description': 'tempo firme', 'icon': '02d'}],
                'pop': 0.2,
                'rain': {'3h': 0},
            })

        return payload

    @staticmethod
    def _empty_forecast_payload():
        return {'list': []}

    def _mocked_requests_get(self, url):
        class FakeResponse:
            def __init__(self, payload, status_code=200):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

        if 'forecast' in url:
            return FakeResponse(self._forecast_payload(date.today()))
        return FakeResponse(self._weather_payload())

    def _mocked_requests_get_empty_forecast(self, url):
        class FakeResponse:
            def __init__(self, payload, status_code=200):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

        if 'forecast' in url:
            return FakeResponse(self._empty_forecast_payload())
        return FakeResponse(self._weather_payload())

    def _mocked_requests_get_forecast_error(self, url):
        class FakeResponse:
            def __init__(self, payload, status_code):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

        if 'forecast' in url:
            return FakeResponse({}, 500)
        return FakeResponse(self._weather_payload(), 200)

    def _mocked_requests_get_partial_today(self, url):
        class FakeResponse:
            def __init__(self, payload, status_code=200):
                self.status_code = status_code
                self._payload = payload

            def json(self):
                return self._payload

        if 'forecast' in url:
            return FakeResponse(self._forecast_payload_partial_today(date.today()))
        return FakeResponse(self._weather_payload())

    @patch('core.views.requests.get')
    def test_invalid_municipio_query_redirects_without_500(self, mock_get):
        mock_get.side_effect = self._mocked_requests_get
        self.client.force_login(self.user)
        response = self.client.get(reverse('previsao_tempo'), {'municipio': 999999})
        self.assertRedirects(response, reverse('previsao_tempo'))

    @patch('core.views.requests.get')
    def test_day_without_forecast_data_does_not_crash(self, mock_get):
        mock_get.side_effect = self._mocked_requests_get
        self.client.force_login(self.user)
        missing_day = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse('previsao_tempo'),
            {'municipio': self.municipio.id, 'dia': missing_day}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clima/previsao_tempo.html')
        self.assertEqual(response.context['previsao_hoje'], [])

    @patch('core.views.requests.get')
    def test_invalid_day_format_falls_back_without_crashing(self, mock_get):
        mock_get.side_effect = self._mocked_requests_get
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('previsao_tempo'),
            {'municipio': self.municipio.id, 'dia': '31-12-2026'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['previsao_hoje'])

    @patch('core.views.requests.get')
    def test_empty_forecast_list_does_not_crash(self, mock_get):
        mock_get.side_effect = self._mocked_requests_get_empty_forecast
        self.client.force_login(self.user)
        response = self.client.get(reverse('previsao_tempo'), {'municipio': self.municipio.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['previsao_cards'], [])
        self.assertEqual(response.context['previsao_hoje'], [])

    @patch('core.views.requests.get')
    def test_forecast_api_non_200_keeps_page_stable(self, mock_get):
        mock_get.side_effect = self._mocked_requests_get_forecast_error
        self.client.force_login(self.user)
        response = self.client.get(reverse('previsao_tempo'), {'municipio': self.municipio.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['previsao_cards'], [])
        self.assertEqual(response.context['previsao_hoje'], [])

    @patch('core.views.requests.get')
    def test_default_selection_prefers_first_full_day(self, mock_get):
        mock_get.side_effect = self._mocked_requests_get_partial_today
        self.client.force_login(self.user)
        response = self.client.get(reverse('previsao_tempo'), {'municipio': self.municipio.id})

        expected_day = date.today() + timedelta(days=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['dia_selecionado'], expected_day)
        self.assertEqual(len(response.context['previsao_hoje']), 8)
        self.assertFalse(response.context['aviso_previsao_parcial'])

    @patch('core.views.requests.get')
    def test_partial_day_shows_warning_context(self, mock_get):
        mock_get.side_effect = self._mocked_requests_get_partial_today
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('previsao_tempo'),
            {
                'municipio': self.municipio.id,
                'dia': date.today().strftime('%Y-%m-%d'),
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['aviso_previsao_parcial'])
        self.assertEqual(response.context['titulo_previsao_dia'], 'Previsão restante do dia')


class ViewPermissionTests(TestCase):
    def setUp(self):
        self.casal_user = User.objects.create_user(
            username='casal',
            password='test123',
            grupo='casal',
        )
        self.seagri_user = User.objects.create_user(
            username='seagri',
            password='test123',
            grupo='seagri',
        )
        self.segov_user = User.objects.create_user(
            username='segov',
            password='test123',
            grupo='segov',
        )

    def test_casal_user_can_access_nova_parada(self):
        self.client.force_login(self.casal_user)
        response = self.client.get(reverse('nova_parada'))
        self.assertEqual(response.status_code, 200)

    def test_segov_user_cannot_access_nova_parada(self):
        self.client.force_login(self.segov_user)
        response = self.client.get(reverse('nova_parada'))
        self.assertRedirects(response, reverse('home'))

    def test_seagri_user_can_access_novo_irrigante(self):
        self.client.force_login(self.seagri_user)
        response = self.client.get(reverse('novo_irrigante'))
        self.assertEqual(response.status_code, 200)

    def test_segov_user_cannot_access_novo_irrigante(self):
        self.client.force_login(self.segov_user)
        response = self.client.get(reverse('novo_irrigante'))
        self.assertRedirects(response, reverse('home'))

    def test_lista_manifestacoes_blocks_user_without_supported_group(self):
        self.client.force_login(self.segov_user)
        response = self.client.get(reverse('lista_manifestacoes'))
        self.assertRedirects(response, reverse('home'))


class DocumentoViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='doc_user',
            password='test123',
            grupo='casal',
        )
        self.categoria_pai = CategoriaDocumento.objects.create(nome='Relatorios')
        self.subcategoria = CategoriaDocumento.objects.create(nome='Mensais', pai=self.categoria_pai)
        self.documento_pai = Documento.objects.create(
            titulo='Relatorio geral',
            descricao='Documento principal',
            arquivo=SimpleUploadedFile('geral.pdf', b'pdf', content_type='application/pdf'),
            categoria=self.categoria_pai,
            cadastrante=self.user,
        )
        self.documento_sub = Documento.objects.create(
            titulo='Relatorio mensal',
            descricao='Documento mensal',
            arquivo=SimpleUploadedFile('mensal.pdf', b'pdf', content_type='application/pdf'),
            categoria=self.subcategoria,
            cadastrante=self.user,
        )
        self.client.force_login(self.user)

    def test_lista_documentos_filters_by_search(self):
        response = self.client.get(reverse('lista_documentos'), {'busca': 'mensal'})
        self.assertEqual(response.status_code, 200)
        documentos = list(response.context['documentos'])
        self.assertEqual(documentos, [self.documento_sub])

    def test_lista_documentos_filters_by_category(self):
        response = self.client.get(reverse('lista_documentos'), {'categoria': self.categoria_pai.id})
        self.assertEqual(response.status_code, 200)
        documentos = list(response.context['documentos'])
        self.assertEqual(documentos, [self.documento_pai])

    def test_documentos_por_categoria_returns_subcategories_and_documents(self):
        response = self.client.get(reverse('documentos_por_categoria', args=[self.categoria_pai.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.subcategoria, list(response.context['subcategorias']))
        self.assertIn(self.documento_pai, list(response.context['documentos']))


class ContadorOuvidoriaTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.casal_user = User.objects.create_user(
            username='casal_count',
            password='test123',
            grupo='casal',
        )
        self.outro_user = User.objects.create_user(
            username='outro_count',
            password='test123',
            grupo='segov',
        )
        Manifestacao.objects.create(
            tipo='denuncia',
            assunto='A',
            descricao='A',
            classificacao='consumo_humano',
            setor_responsavel='CASAL',
            protocolo='CONT001',
            status='recebido',
        )
        Manifestacao.objects.create(
            tipo='denuncia',
            assunto='B',
            descricao='B',
            classificacao='consumo_humano',
            setor_responsavel='CASAL',
            protocolo='CONT002',
            status='em_analise',
        )
        antiga = Manifestacao.objects.create(
            tipo='denuncia',
            assunto='C',
            descricao='C',
            classificacao='consumo_humano',
            setor_responsavel='CASAL',
            protocolo='CONT003',
            status='concluido',
        )
        antiga.ultima_atualizacao = timezone.now() - timedelta(days=8)
        antiga.save(update_fields=['ultima_atualizacao'])

    def test_contador_ouvidoria_respects_sector_and_recent_items(self):
        request = self.factory.get('/')
        request.user = self.casal_user
        context = contador_ouvidoria(request)

        self.assertEqual(context['total_manifestacoes'], 3)
        self.assertEqual(context['recebido'], 1)
        self.assertEqual(context['em_analise'], 1)
        self.assertEqual(context['encaminhado'], 0)

    def test_contador_ouvidoria_returns_empty_for_unsupported_group(self):
        request = self.factory.get('/')
        request.user = self.outro_user
        self.assertEqual(contador_ouvidoria(request), {})
