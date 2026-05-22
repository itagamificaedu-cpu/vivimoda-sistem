"""
Tarefas agendadas do módulo Financeiro.
Executadas via Celery Beat (scheduler).
"""
from celery import shared_task
from django.utils import timezone
from datetime import date
import logging

logger = logging.getLogger(__name__)


@shared_task(name='financeiro.marcar_contas_vencidas')
def marcar_contas_vencidas():
    """
    Marca contas a receber e a pagar PENDENTES como VENCIDAS
    quando a data de vencimento for anterior a hoje.
    Roda diariamente às 00h05.
    """
    from .models import ContaReceber, ContaPagar
    hoje = date.today()

    # Contas a receber vencidas
    cr_atualizadas = ContaReceber.objects.filter(
        status='PENDENTE',
        data_vencimento__lt=hoje
    ).update(status='VENCIDO')

    # Contas a pagar vencidas
    cp_atualizadas = ContaPagar.objects.filter(
        status='PENDENTE',
        data_vencimento__lt=hoje
    ).update(status='VENCIDO')

    logger.info(
        f'[Financeiro] Contas vencidas marcadas: '
        f'{cr_atualizadas} a receber / {cp_atualizadas} a pagar'
    )
    return {'receber': cr_atualizadas, 'pagar': cp_atualizadas}


@shared_task(name='financeiro.calcular_juros_automatico')
def calcular_juros_automatico():
    """
    Recalcula juros e multa de contas vencidas com base na
    configuração do sistema. Roda diariamente às 00h10.
    """
    from .models import ContaReceber
    from apps.core.utils import calcular_juros_simples, calcular_multa

    try:
        from apps.configuracoes.models import ConfiguracaoLoja
        config = ConfiguracaoLoja.get_config()
        taxa_juros = config.taxa_juros_mes
        perc_multa = config.percentual_multa
        carencia = config.carencia_juros_dias
    except Exception:
        from decimal import Decimal
        taxa_juros = Decimal('2')
        perc_multa = Decimal('2')
        carencia = 3

    contas_vencidas = ContaReceber.objects.filter(status='VENCIDO')
    atualizadas = 0

    for conta in contas_vencidas:
        dias = conta.dias_atraso
        if dias > carencia:
            juros = calcular_juros_simples(conta.valor_pendente, taxa_juros, dias)
            multa = calcular_multa(conta.valor_pendente, perc_multa)
            if conta.valor_juros != juros or conta.valor_multa != multa:
                conta.valor_juros = juros
                conta.valor_multa = multa
                conta.save(update_fields=['valor_juros', 'valor_multa'])
                atualizadas += 1

    logger.info(f'[Financeiro] Juros recalculados em {atualizadas} contas vencidas.')
    return {'atualizadas': atualizadas}
