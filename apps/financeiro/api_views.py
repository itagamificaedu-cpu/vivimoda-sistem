"""
Views AJAX de Financeiro.
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from datetime import date
from .models import ContaReceber, ContaPagar


@login_required
def resumo_financeiro(request):
    """
    GET /api/financeiro/resumo/
    Retorna totais de contas a receber e a pagar para o dashboard.
    """
    hoje = date.today()

    a_receber = ContaReceber.objects.filter(
        status__in=['PENDENTE', 'PARCIAL']
    ).aggregate(t=Sum('valor_pendente'))['t'] or 0

    vencidas_receber = ContaReceber.objects.filter(
        status__in=['PENDENTE', 'PARCIAL'],
        data_vencimento__lt=hoje
    ).aggregate(t=Sum('valor_pendente'))['t'] or 0

    a_pagar = ContaPagar.objects.filter(
        status__in=['PENDENTE', 'PARCIAL']
    ).aggregate(t=Sum('valor_pendente'))['t'] or 0

    return JsonResponse({
        'a_receber': float(a_receber),
        'vencidas_receber': float(vencidas_receber),
        'a_pagar': float(a_pagar),
    })
