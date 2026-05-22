"""
Views AJAX de Caixa — consulta de sessão ativa e saldo.
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Caixa, SessaoCaixa


@login_required
def sessao_ativa(request):
    """
    GET /api/caixa/sessao-ativa/
    Retorna a sessão aberta do operador atual, se existir.
    """
    sessao = SessaoCaixa.objects.filter(
        operador=request.user, status='ABERTO'
    ).select_related('caixa').first()

    if not sessao:
        return JsonResponse({'sessao': None})

    return JsonResponse({
        'sessao': {
            'id': sessao.pk,
            'caixa': str(sessao.caixa),
            'abertura': sessao.data_abertura.strftime('%d/%m/%Y %H:%M'),
            'total_vendas': float(sessao.total_vendas),
        }
    })


@login_required
def saldo_sessao(request, sessao_pk):
    """
    GET /api/caixa/saldo/<sessao_pk>/
    Retorna o saldo esperado da sessão de caixa.
    """
    try:
        sessao = SessaoCaixa.objects.get(pk=sessao_pk)
    except SessaoCaixa.DoesNotExist:
        return JsonResponse({'erro': 'Sessão não encontrada'}, status=404)

    return JsonResponse({
        'sessao_id': sessao.pk,
        'saldo_esperado': float(sessao.saldo_esperado),
        'total_dinheiro': float(sessao.total_dinheiro),
        'total_pix': float(sessao.total_pix),
        'total_credito': float(sessao.total_credito),
        'total_debito': float(sessao.total_debito),
        'total_vendas': float(sessao.total_vendas),
    })
