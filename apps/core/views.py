"""
Views do core — dashboard e endpoints AJAX utilitários.
"""
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta

from .mixins import LoginObrigatorioMixin
from .utils import buscar_cep, buscar_cnpj


@method_decorator(login_required, name='dispatch')
class DashboardView(LoginObrigatorioMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        ctx['hoje'] = hoje
        ctx['titulo'] = 'Dashboard'
        return ctx


@login_required
def ajax_buscar_cep(request):
    cep = request.GET.get('cep', '')
    dados = buscar_cep(cep)
    if dados:
        return JsonResponse({'ok': True, 'dados': dados})
    return JsonResponse({'ok': False, 'mensagem': 'CEP não encontrado.'})


@login_required
def ajax_buscar_cnpj(request):
    cnpj = request.GET.get('cnpj', '')
    dados = buscar_cnpj(cnpj)
    if dados:
        return JsonResponse({'ok': True, 'dados': dados})
    return JsonResponse({'ok': False, 'mensagem': 'CNPJ não encontrado.'})


@login_required
def ajax_dashboard_dados(request):
    """Retorna dados do dashboard via AJAX (atualização a cada 5 min)."""
    hoje = timezone.localdate()
    inicio_mes = hoje.replace(day=1)

    dados = {}

    # Importações condicionais para evitar erros se módulos não existirem
    try:
        from apps.vendas.models import Venda
        dados['vendas_hoje'] = Venda.objects.filter(
            data_venda__date=hoje,
            status__in=['PAGO', 'PARCIAL']
        ).aggregate(total=Sum('valor_total'))['total'] or 0

        dados['ultimas_vendas'] = list(
            Venda.objects.filter(status__in=['PAGO', 'PARCIAL', 'PENDENTE'])
            .select_related('cliente', 'vendedor')
            .order_by('-criado_em')[:10]
            .values('numero', 'cliente__nome', 'valor_total', 'status', 'criado_em')
        )
    except Exception:
        dados['vendas_hoje'] = 0
        dados['ultimas_vendas'] = []

    try:
        from apps.financeiro.models import ContaReceber, ContaPagar
        dados['contas_vencer_hoje'] = ContaReceber.objects.filter(
            data_vencimento=hoje, status='PENDENTE'
        ).count()
        dados['parcelas_vencidas'] = ContaReceber.objects.filter(
            data_vencimento__lt=hoje, status__in=['PENDENTE', 'PARCIAL']
        ).count()
    except Exception:
        dados['contas_vencer_hoje'] = 0
        dados['parcelas_vencidas'] = 0

    try:
        from apps.produtos.models import Produto
        dados['estoque_minimo'] = Produto.objects.filter(
            ativo=True
        ).count()  # placeholder, refinado no módulo estoque
    except Exception:
        dados['estoque_minimo'] = 0

    dados['data_hora'] = timezone.localtime().strftime('%d/%m/%Y %H:%M')
    return JsonResponse(dados)
