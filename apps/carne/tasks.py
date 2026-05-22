"""
Tarefas agendadas do módulo Carnê/Crediário.
"""
from celery import shared_task
from datetime import date
import logging

logger = logging.getLogger(__name__)


@shared_task(name='carne.marcar_parcelas_vencidas')
def marcar_parcelas_vencidas():
    """
    Marca parcelas PENDENTES como VENCIDAS quando passam do vencimento.
    Roda diariamente às 00h01.
    """
    from .models import ParcelaCarne
    hoje = date.today()

    atualizadas = ParcelaCarne.objects.filter(
        status='PENDENTE',
        data_vencimento__lt=hoje
    ).update(status='VENCIDO')

    logger.info(f'[Carnê] {atualizadas} parcela(s) marcada(s) como vencida(s).')
    return {'atualizadas': atualizadas}


@shared_task(name='carne.notificar_vencimentos_proximos')
def notificar_vencimentos_proximos():
    """
    Envia notificação interna para carnês que vencem em 3 dias.
    Roda diariamente às 08h00.
    """
    from .models import ParcelaCarne
    from datetime import timedelta

    hoje = date.today()
    limite = hoje + timedelta(days=3)

    proximas = ParcelaCarne.objects.filter(
        status='PENDENTE',
        data_vencimento__range=[hoje, limite]
    ).select_related('carne__cliente')

    count = proximas.count()
    logger.info(f'[Carnê] {count} parcela(s) vencem nos próximos 3 dias.')
    return {'proximas': count}
