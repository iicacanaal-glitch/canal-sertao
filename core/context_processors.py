from django.db.models import Count
from .models import Manifestacao
from django.utils import timezone
from datetime import timedelta


def contador_ouvidoria(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user

    if user.grupo =='seagri':
        qs = Manifestacao.objects.filter(setor_responsavel='SEAGRI')

    elif user.grupo == 'casal':
        qs = Manifestacao.objects.filter(setor_responsavel='CASAL')

    else:
        return {}

    limite = timezone.now() - timedelta(days=7)

    qs = qs.exclude(
        status='concluido',
        ultima_atualizacao__lt=limite
    )

    resumo = qs.values('status').annotate(total=Count('id'))

    # transforma em dicionário
    resumo_dict = {item['status']: item['total'] for item in resumo}

    return {
        'total_manifestacoes': sum(resumo_dict.values()),
        'recebido': resumo_dict.get('recebido', 0),
        'em_analise': resumo_dict.get('em_analise', 0),
        'encaminhado': resumo_dict.get('encaminhado', 0),
        'em_andamento': resumo_dict.get('em_andamento', 0),
    }
