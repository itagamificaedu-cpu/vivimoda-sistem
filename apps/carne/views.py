from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from datetime import date

from .models import Carne, ParcelaCarne
from apps.core.utils import gerar_numero_sequencial, calcular_juros_simples, calcular_multa


@login_required
def lista(request):
    qs = Carne.objects.select_related('cliente').all()
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if q:
        qs = qs.filter(Q(numero__icontains=q) | Q(cliente__nome__icontains=q))
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'carne/lista.html', {
        'titulo': 'Carnês / Crediário',
        'page_obj': page, 'q': q, 'status': status,
        'status_choices': Carne.STATUS,
        'total': qs.count(),
    })


@login_required
def detalhe(request, pk):
    carne = get_object_or_404(Carne.objects.select_related('cliente', 'venda'), pk=pk)
    parcelas = carne.parcelas.all()
    return render(request, 'carne/detalhe.html', {
        'titulo': f'Carnê {carne.numero}',
        'carne': carne, 'parcelas': parcelas,
    })


@login_required
def novo(request):
    """Cria carnê avulso (sem venda vinculada)."""
    from apps.clientes.models import Cliente
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        valor_total = Decimal(request.POST.get('valor_total', '0'))
        entrada = Decimal(request.POST.get('entrada', '0'))
        qtd_parcelas = int(request.POST.get('quantidade_parcelas', 1))
        dia_venc = int(request.POST.get('dia_vencimento', 10))
        taxa_juros = Decimal(request.POST.get('taxa_juros', '0'))
        observacoes = request.POST.get('observacoes', '')

        valor_financiado = valor_total - entrada
        valor_parcela = (valor_financiado / qtd_parcelas).quantize(Decimal('0.01'))

        carne = Carne.objects.create(
            numero=gerar_numero_sequencial(Carne, 'numero', 'CR', 6),
            cliente_id=cliente_id,
            valor_total=valor_total,
            entrada=entrada,
            quantidade_parcelas=qtd_parcelas,
            valor_parcela=valor_parcela,
            dia_vencimento=dia_venc,
            taxa_juros=taxa_juros,
            observacoes=observacoes,
            usuario=request.user,
        )
        carne.gerar_parcelas()

        messages.success(request, f'Carnê {carne.numero} criado com {qtd_parcelas} parcelas!')
        return redirect('carne:detalhe', pk=carne.pk)

    clientes = Cliente.objects.filter(ativo=True).order_by('nome')
    return render(request, 'carne/form.html', {
        'titulo': 'Novo Carnê', 'clientes': clientes,
    })


@login_required
def baixar_parcela(request, pk):
    """Registra pagamento de uma parcela."""
    parcela = get_object_or_404(ParcelaCarne.objects.select_related('carne__cliente'), pk=pk)

    if request.method == 'POST':
        valor_pago = Decimal(request.POST.get('valor_pago', '0'))
        forma = request.POST.get('forma_pagamento', 'DINHEIRO')
        desconto_aplicado = Decimal(request.POST.get('desconto', '0'))

        # Aplica juros/multa se vencida
        config = _get_config()
        if parcela.dias_atraso > 0:
            carencia = config.carencia_juros_dias if config else 3
            if parcela.dias_atraso > carencia:
                parcela.valor_juros = calcular_juros_simples(
                    parcela.valor_original,
                    config.taxa_juros_mes if config else Decimal('2'),
                    parcela.dias_atraso
                )
                parcela.valor_multa = calcular_multa(
                    parcela.valor_original,
                    config.percentual_multa if config else Decimal('2')
                )

        parcela.valor_desconto = desconto_aplicado
        parcela.valor_pago = valor_pago
        parcela.forma_pagamento = forma
        parcela.data_pagamento = date.today()
        parcela.status = 'PAGO'
        parcela.usuario_baixa = request.user

        # Vincula à sessão de caixa aberta
        from apps.caixa.models import SessaoCaixa
        sessao = SessaoCaixa.objects.filter(operador=request.user, status='ABERTO').first()
        parcela.sessao_caixa = sessao
        parcela.save()

        # Verifica se carnê foi quitado
        pendentes = parcela.carne.parcelas.exclude(status__in=['PAGO','CANCELADO']).count()
        if pendentes == 0:
            parcela.carne.status = 'QUITADO'
            parcela.carne.save(update_fields=['status'])

        # Atualiza saldo do cliente
        _atualizar_saldo_cliente(parcela.carne.cliente)

        messages.success(request, f'Parcela {parcela.numero} baixada — R$ {valor_pago}')
        return redirect('carne:detalhe', pk=parcela.carne.pk)

    # Calcula juros e multa sugeridos para pré-preencher o template
    config = _get_config()
    juros_sugerido = Decimal('0')
    multa_sugerida = Decimal('0')

    if parcela.dias_atraso > 0:
        carencia = config.carencia_juros_dias if config else 3
        if parcela.dias_atraso > carencia:
            juros_sugerido = calcular_juros_simples(
                parcela.valor_original,
                config.taxa_juros_mes if config else Decimal('2'),
                parcela.dias_atraso,
            )
            multa_sugerida = calcular_multa(
                parcela.valor_original,
                config.percentual_multa if config else Decimal('2'),
            )

    return render(request, 'carne/baixar_parcela.html', {
        'titulo': f'Baixar Parcela {parcela.numero}',
        'parcela': parcela,
        'config': config,
        'juros_sugerido': juros_sugerido,
        'multa_sugerida': multa_sugerida,
    })


@login_required
def imprimir_carne(request, pk):
    """Imprime o carnê em formato PDF-friendly."""
    carne = get_object_or_404(Carne.objects.select_related('cliente'), pk=pk)
    parcelas = carne.parcelas.all()
    try:
        from apps.configuracoes.models import ConfiguracaoLoja
        config = ConfiguracaoLoja.get_config()
    except Exception:
        config = None
    return render(request, 'carne/imprimir.html', {
        'carne': carne, 'parcelas': parcelas, 'config': config,
    })


@login_required
def renegociar(request, pk):
    """Renegocia um carnê — cria novo substituindo o anterior."""
    carne = get_object_or_404(Carne, pk=pk)

    if request.method == 'POST':
        novo_qtd = int(request.POST.get('quantidade_parcelas', carne.quantidade_parcelas))
        novo_dia = int(request.POST.get('dia_vencimento', carne.dia_vencimento))
        taxa = Decimal(request.POST.get('taxa_juros', str(carne.taxa_juros)))
        obs = request.POST.get('observacoes', '')

        saldo = carne.valor_pendente
        novo_valor_parcela = (saldo / novo_qtd).quantize(Decimal('0.01'))

        novo_carne = Carne.objects.create(
            numero=gerar_numero_sequencial(Carne, 'numero', 'CR', 6),
            cliente=carne.cliente,
            venda=carne.venda,
            valor_total=saldo,
            quantidade_parcelas=novo_qtd,
            valor_parcela=novo_valor_parcela,
            dia_vencimento=novo_dia,
            taxa_juros=taxa,
            carne_original=carne,
            observacoes=obs,
            usuario=request.user,
        )
        novo_carne.gerar_parcelas()

        # Cancela o carnê original
        carne.status = 'RENEGOCIADO'
        carne.save(update_fields=['status'])

        messages.success(request, f'Carnê renegociado! Novo carnê: {novo_carne.numero}')
        return redirect('carne:detalhe', pk=novo_carne.pk)

    return render(request, 'carne/renegociar.html', {
        'titulo': f'Renegociar Carnê {carne.numero}', 'carne': carne,
    })


def _get_config():
    try:
        from apps.configuracoes.models import ConfiguracaoLoja
        return ConfiguracaoLoja.get_config()
    except Exception:
        return None


def _atualizar_saldo_cliente(cliente):
    from apps.financeiro.models import ContaReceber
    from django.db.models import Sum
    total = ContaReceber.objects.filter(
        cliente=cliente, status__in=['PENDENTE', 'PARCIAL', 'VENCIDO']
    ).aggregate(t=Sum('valor_pendente'))['t'] or 0
    cliente.saldo_devedor = total
    cliente.save(update_fields=['saldo_devedor'])
