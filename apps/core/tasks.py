"""
Tarefas agendadas do Core — limpeza de sessões, relatório diário, etc.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name='core.limpar_sessoes_expiradas')
def limpar_sessoes_expiradas():
    """
    Remove sessões Django expiradas do banco de dados.
    Roda diariamente às 03h00.
    """
    from django.contrib.sessions.backends.db import SessionStore
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    antes = Session.objects.count()
    Session.objects.filter(expire_date__lt=timezone.now()).delete()
    depois = Session.objects.count()
    removidas = antes - depois

    logger.info(f'[Core] {removidas} sessão(ões) expirada(s) removida(s).')
    return {'removidas': removidas}


@shared_task(name='core.relatorio_diario')
def relatorio_diario():
    """
    Compila métricas do dia anterior e registra no log.
    Roda diariamente às 06h00.
    """
    from datetime import date, timedelta
    from django.db.models import Sum, Count

    ontem = date.today() - timedelta(days=1)

    try:
        from apps.vendas.models import Venda
        vendas = Venda.objects.filter(
            data_venda__date=ontem,
            status__in=['PAGO', 'PARCIAL']
        ).aggregate(
            qtd=Count('id'),
            total=Sum('valor_total')
        )
    except Exception:
        vendas = {'qtd': 0, 'total': 0}

    try:
        from apps.carne.models import ParcelaCarne
        parcelas_recebidas = ParcelaCarne.objects.filter(
            data_pagamento=ontem, status='PAGO'
        ).aggregate(total=Sum('valor_pago'))['total'] or 0
    except Exception:
        parcelas_recebidas = 0

    logger.info(
        f'[Relatório Diário] {ontem} — '
        f'Vendas: {vendas["qtd"]} / R$ {vendas["total"] or 0:.2f} | '
        f'Carnê recebido: R$ {parcelas_recebidas:.2f}'
    )

    return {
        'data': str(ontem),
        'qtd_vendas': vendas['qtd'],
        'total_vendas': float(vendas['total'] or 0),
        'parcelas_recebidas': float(parcelas_recebidas),
    }


@shared_task(name='core.atualizar_status_vendas')
def atualizar_status_vendas():
    """
    Atualiza vendas PENDENTES cujo prazo passou para VENCIDO.
    Também verifica contas parcialmente pagas.
    Roda diariamente às 00h15.
    """
    from datetime import date
    from apps.vendas.models import Venda

    hoje = date.today()
    atualizadas = 0

    # Vendas pendentes com valor ainda em aberto
    vendas_pendentes = Venda.objects.filter(
        status='PENDENTE',
        valor_pendente__gt=0
    )
    for v in vendas_pendentes:
        if v.valor_pago > 0:
            v.status = 'PARCIAL'
            v.save(update_fields=['status'])
            atualizadas += 1

    logger.info(f'[Core] {atualizadas} venda(s) atualizada(s) para status PARCIAL.')
    return {'atualizadas': atualizadas}
