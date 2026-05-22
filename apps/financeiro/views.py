from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q, Sum
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from decimal import Decimal

from .models import ContaReceber, ContaPagar, LancamentoFinanceiro, ContaBancaria, PlanoContas
from apps.core.utils import gerar_numero_sequencial, calcular_juros_simples, calcular_multa


@login_required
def receber(request):
    """Listagem de contas a receber."""
    qs = ContaReceber.objects.select_related('cliente').all()
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    vencimento = request.GET.get('vencimento', '')

    if q:
        qs = qs.filter(Q(cliente__nome__icontains=q) | Q(numero__icontains=q))
    if status:
        qs = qs.filter(status=status)
    if vencimento == 'hoje':
        qs = qs.filter(data_vencimento=date.today())
    elif vencimento == 'semana':
        qs = qs.filter(data_vencimento__lte=date.today() + timedelta(days=7))
    elif vencimento == 'vencido':
        qs = qs.filter(data_vencimento__lt=date.today(), status__in=['PENDENTE','PARCIAL'])

    # Totais para o resumo
    total_pendente = qs.filter(status__in=['PENDENTE','PARCIAL']).aggregate(t=Sum('valor_pendente'))['t'] or 0
    total_vencido = qs.filter(
        status__in=['PENDENTE','PARCIAL'], data_vencimento__lt=date.today()
    ).aggregate(t=Sum('valor_pendente'))['t'] or 0

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'financeiro/receber.html', {
        'titulo': 'Contas a Receber',
        'page_obj': page, 'q': q, 'status': status, 'vencimento': vencimento,
        'total_pendente': total_pendente, 'total_vencido': total_vencido,
        'status_choices': ContaReceber.STATUS,
    })


@login_required
def baixar_recebimento(request, pk):
    """Baixa (pagamento) de uma conta a receber."""
    conta = get_object_or_404(ContaReceber, pk=pk)

    if request.method == 'POST':
        valor_pago = Decimal(request.POST.get('valor_pago', '0'))
        forma = request.POST.get('forma', 'DINHEIRO')
        data_pag = request.POST.get('data_pagamento') or str(date.today())

        # Aplica juros/multa se houver atraso
        config = _get_config()
        dias_at = conta.dias_atraso
        if dias_at > (config.carencia_juros_dias if config else 3):
            conta.valor_juros = calcular_juros_simples(
                conta.valor_pendente,
                config.taxa_juros_mes if config else Decimal('2'),
                dias_at
            )
            conta.valor_multa = calcular_multa(
                conta.valor_pendente,
                config.percentual_multa if config else Decimal('2')
            )

        conta.valor_pago += valor_pago
        conta.forma_recebimento = forma
        conta.data_pagamento = data_pag

        valor_total_due = conta.valor_original + conta.valor_juros + conta.valor_multa - conta.valor_desconto
        if conta.valor_pago >= valor_total_due:
            conta.status = 'PAGO'
        elif conta.valor_pago > 0:
            conta.status = 'PARCIAL'

        conta.save()

        # Atualiza saldo devedor do cliente
        _atualizar_saldo_cliente(conta.cliente)

        messages.success(request, f'Recebimento de R$ {valor_pago} registrado!')
        return redirect('financeiro:receber')

    config = _get_config()
    return render(request, 'financeiro/baixar_recebimento.html', {
        'titulo': 'Baixar Recebimento',
        'conta': conta,
        'config': config,
    })


@login_required
def pagar(request):
    """Listagem de contas a pagar."""
    qs = ContaPagar.objects.select_related('fornecedor').all()
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if q:
        qs = qs.filter(Q(fornecedor__razao_social__icontains=q) | Q(numero__icontains=q) | Q(descricao__icontains=q))
    if status:
        qs = qs.filter(status=status)

    total_pendente = qs.filter(status__in=['PENDENTE','PARCIAL']).aggregate(t=Sum('valor_pendente'))['t'] or 0
    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'financeiro/pagar.html', {
        'titulo': 'Contas a Pagar',
        'page_obj': page, 'q': q, 'status': status,
        'total_pendente': total_pendente,
        'status_choices': ContaPagar.STATUS,
    })


@login_required
def baixar_pagamento(request, pk):
    conta = get_object_or_404(ContaPagar, pk=pk)
    if request.method == 'POST':
        valor = Decimal(request.POST.get('valor_pago', '0'))
        forma = request.POST.get('forma', 'DINHEIRO')
        conta.valor_pago += valor
        conta.forma_pagamento = forma
        conta.data_pagamento = date.today()
        if conta.valor_pago >= conta.valor_original:
            conta.status = 'PAGO'
        else:
            conta.status = 'PARCIAL'
        conta.save()
        messages.success(request, f'Pagamento de R$ {valor} registrado!')
        return redirect('financeiro:pagar')

    return render(request, 'financeiro/baixar_pagamento.html', {
        'titulo': 'Registrar Pagamento', 'conta': conta,
    })


@login_required
def lancamentos(request):
    """Lançamentos avulsos de receitas e despesas."""
    qs = LancamentoFinanceiro.objects.select_related('plano_contas', 'conta_bancaria').all()
    tipo = request.GET.get('tipo', '')
    if tipo:
        qs = qs.filter(tipo=tipo)

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    receitas = qs.filter(tipo='RECEITA', status='REALIZADO').aggregate(t=Sum('valor'))['t'] or 0
    despesas = qs.filter(tipo='DESPESA', status='REALIZADO').aggregate(t=Sum('valor'))['t'] or 0

    return render(request, 'financeiro/lancamentos.html', {
        'titulo': 'Lançamentos Financeiros',
        'page_obj': page, 'tipo': tipo,
        'receitas': receitas, 'despesas': despesas,
        'saldo': receitas - despesas,
        'planos': PlanoContas.objects.filter(ativo=True),
        'contas': ContaBancaria.objects.filter(ativo=True),
    })


@login_required
def novo_lancamento(request):
    if request.method == 'POST':
        from .forms import FormLancamento
        form = FormLancamento(request.POST, request.FILES)
        if form.is_valid():
            lanc = form.save(commit=False)
            lanc.usuario = request.user
            lanc.save()
            messages.success(request, 'Lançamento registrado!')
            return redirect('financeiro:lancamentos')
    return redirect('financeiro:lancamentos')


@login_required
def fluxo_caixa(request):
    """Relatório de fluxo de caixa."""
    hoje = date.today()
    inicio = date(hoje.year, hoje.month, 1)
    fim_str = request.GET.get('fim', str(hoje))
    inicio_str = request.GET.get('inicio', str(inicio))

    try:
        inicio = date.fromisoformat(inicio_str)
        fim = date.fromisoformat(fim_str)
    except ValueError:
        fim = hoje

    receber_qs = ContaReceber.objects.filter(
        data_vencimento__range=[inicio, fim]
    ).values('data_vencimento').annotate(total=Sum('valor_pendente'))

    pagar_qs = ContaPagar.objects.filter(
        data_vencimento__range=[inicio, fim]
    ).values('data_vencimento').annotate(total=Sum('valor_pendente'))

    return render(request, 'financeiro/fluxo_caixa.html', {
        'titulo': 'Fluxo de Caixa',
        'inicio': inicio, 'fim': fim,
        'receber': list(receber_qs),
        'pagar': list(pagar_qs),
    })


# ---- Auxiliares ----

def _get_config():
    try:
        from apps.configuracoes.models import ConfiguracaoLoja
        return ConfiguracaoLoja.get_config()
    except Exception:
        return None


def _atualizar_saldo_cliente(cliente):
    total_devedor = ContaReceber.objects.filter(
        cliente=cliente, status__in=['PENDENTE', 'PARCIAL', 'VENCIDO']
    ).aggregate(t=Sum('valor_pendente'))['t'] or 0
    cliente.saldo_devedor = total_devedor
    cliente.save(update_fields=['saldo_devedor'])


@login_required
def nova_conta_receber(request):
    """Cria conta a receber avulsa."""
    if request.method == 'POST':
        from apps.core.utils import gerar_numero_sequencial
        cr = ContaReceber.objects.create(
            numero=gerar_numero_sequencial(ContaReceber, 'numero', 'CR', 6),
            cliente_id=request.POST.get('cliente_id') or None,
            descricao=request.POST.get('descricao', ''),
            valor=Decimal(request.POST.get('valor', '0')),
            data_emissao=request.POST.get('data_emissao') or date.today(),
            data_vencimento=request.POST.get('data_vencimento', str(date.today())),
            observacoes=request.POST.get('observacoes', ''),
            usuario=request.user,
        )
        messages.success(request, f'Conta a receber {cr.numero} criada!')
        return redirect('financeiro:receber')
    return redirect('financeiro:receber')


@login_required
def editar_conta_receber(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk)
    if request.method == 'POST':
        conta.descricao = request.POST.get('descricao', conta.descricao)
        conta.valor = Decimal(request.POST.get('valor', str(conta.valor)))
        conta.data_vencimento = request.POST.get('data_vencimento', str(conta.data_vencimento))
        conta.save()
        messages.success(request, 'Conta a receber atualizada!')
    return redirect('financeiro:receber')


@login_required
def nova_conta_pagar(request):
    """Cria conta a pagar avulsa."""
    if request.method == 'POST':
        from apps.core.utils import gerar_numero_sequencial
        cp = ContaPagar.objects.create(
            numero=gerar_numero_sequencial(ContaPagar, 'numero', 'CP', 6),
            fornecedor_id=request.POST.get('fornecedor_id') or None,
            descricao=request.POST.get('descricao', ''),
            valor=Decimal(request.POST.get('valor', '0')),
            data_emissao=request.POST.get('data_emissao') or date.today(),
            data_vencimento=request.POST.get('data_vencimento', str(date.today())),
            observacoes=request.POST.get('observacoes', ''),
            usuario=request.user,
        )
        messages.success(request, f'Conta a pagar {cp.numero} criada!')
        return redirect('financeiro:pagar')
    return redirect('financeiro:pagar')


@login_required
def editar_conta_pagar(request, pk):
    conta = get_object_or_404(ContaPagar, pk=pk)
    if request.method == 'POST':
        conta.descricao = request.POST.get('descricao', conta.descricao)
        conta.valor = Decimal(request.POST.get('valor', str(conta.valor)))
        conta.data_vencimento = request.POST.get('data_vencimento', str(conta.data_vencimento))
        conta.save()
        messages.success(request, 'Conta a pagar atualizada!')
    return redirect('financeiro:pagar')
