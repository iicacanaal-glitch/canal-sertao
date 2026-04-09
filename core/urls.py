from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),

    path('paradas/', views.lista_paradas, name='lista_paradas'),
    path('paradas/nova/', views.nova_parada, name='nova_parada'),

    path('irrigantes/', views.lista_irrigantes, name='lista_irrigantes'),
    path('irrigantes/novo/', views.novo_irrigante, name='novo_irrigante'),

    path('previsao-tempo/', views.previsao_tempo, name='previsao_tempo'),

    path('documentos/', views.lista_documentos, name='lista_documentos'),
    path('documentos/novo/', views.novo_documento, name='novo_documento'),
    path('documentos/<int:documento_id>/', views.detalhe_documento, name='detalhe_documento'),
    path('documentos/<int:documento_id>/editar/', views.editar_documento, name='editar_documento'),
    path('documentos/<int:documento_id>/excluir/', views.excluir_documento, name='excluir_documento'),

    path('categorias/nova/', views.nova_categoria, name='nova_categoria'),
    path('categorias/<int:categoria_id>/', views.documentos_por_categoria, name='documentos_por_categoria'),

    path('mapeamento/mapa-canal/', views.mapa_canal, name='mapa_canal'),
    path('mapeamento/mapa-solos/', views.mapa_solos, name='mapa_solos'),
    path('mapeamento/culturas/', views.mapa_culturas, name='mapa_culturas'),

    path('projetos/', views.lista_projetos, name='lista_projetos'),
    path('projetos/novo/', views.cadastrar_projeto, name='cadastrar_projeto'),
]
