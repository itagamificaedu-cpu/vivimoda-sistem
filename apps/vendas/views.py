"""
Views de Vendas: listagem, PDV completo, pagamento, cancelamento, devolução.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q, Sum
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
from datetime import date

from .models import Venda, ItemVenda, PagamentoVenda
from apps.core.utils import gerar_numero_sequencial


@login_required
def lista(request):
    qs = Venda.objects.select_related('cliente', 'vendedor', 'usuario').all()
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    periodo = request.GET.get('periodo', 'hoje')

    if q:
        qs = qs.filter(Q(numero__icontains=q) | Q(cliente__nome__icontains=q))
    if status:
        qs = qs.filter(status=status)
    if periodo == 'hoje':
        qs = qs.filter(data_venda__date=date.today())
    elif periodo == 'semana':
        from datetime import timedelta
        qs = qs.filter(data_venda__date__gte=date.today() - timedelta(days=7))
    elif periodo == 'mes':
        qs = qs.filter(data_venda__year=date.today().year, data_venda__month=date.today().month)

    total_valor = qs.filter(status__in=['PAGO', 'PARCIAL']).aggregate(t=Sum('valor_total'))['t'] or 0

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'vendas/lista.html', {
        'titulo': 'Vendas',
        'page_obj': page, 'q': q, 'status': status, 'periodo': periodo,
        'total_valor': total_valor, 'total': qs.count(),
        'status_choices': Venda.STATUS,
    })


@login_required
def pdv(request):
    """Tela do PDV — ponto de venda."""
    # Verifica se há caixa aberto para este usuário
    from apps.caixa.models import SessaoCaixa
    sessao_caixa = SessaoCaixa.objects.filter(
        operador=request.user, status='ABERTO'
    ).first()

    # Busca vendedor vinculado ao usuário
    vendedor = None
    try:
        vendedor = request.user.funcionario
    except Exception:
        pass

    return render(request, 'vendas/pdv.html', {
        'titulo': 'PDV — Ponto de Venda',
        'sessao_caixa': sessao_caixa,
        'vendedor': vendedor,
        'formas_pagamento': PagamentoVenda.FORMAS,
    })


@login_required
def finalizar_venda(request):
    """Processa o POST do PDV e cria a venda com itens e pagamentos."""
    if request.method != 'POST':
        return redirect('vendas:pdv')

    import json
    try:
        dados = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': False, 'mensagem': 'Dados inválidos.'}, status=400)

    cliente_id = dados.get('cliente_id')
    itens_data = dados.get('itens', [])
    pagamentos_data = dados.get('pagamentos', [])
    desconto_global = Decimal(str(dados.get('desconto', '0')))
    observacoes = dados.get('observacoes', '')
    canal = dados.get('canal', 'LOJA')

    if not itens_data:
        return JsonResponse({'ok': False, 'mensagem': 'Adicione pelo menos um produto.'})

    # Verifica caixa aberto
    from apps.caixa.models import SessaoCaixa, MovimentacaoCaixa
    sessao_caixa = SessaoCaixa.objects.filter(operador=request.user, status='ABERTO').first()

    # Cria a venda
    venda = Venda.objects.create(
        numero=gerar_numero_sequencial(Venda, 'numero', 'VD', 6),
        cliente_id=cliente_id or None,
        valor_desconto=desconto_global,
        observacoes=observacoes,
        canal=canal,
        status='PENDENTE',
        usuario=request.user,
        caixa=sessao_caixa,
    )

    # Vincula vendedor
    try:
        venda.vendedor = request.user.funcionario
        venda.save(update_fields=['vendedor'])
    except Exception:
        pass

    # Adiciona itens e baixa estoque
    from apps.produtos.models import Produto, GradeProduto
    from apps.estoque.models import MovimentacaoEstoque

    for item_data in itens_data:
        produto = Produto.objects.get(pk=item_data['produto_id'])
        grade = None
        if item_data.get('grade_id'):
            grade = GradeProduto.objects.get(pk=item_data['grade_id'])

        quantidade = Decimal(str(item_data['quantidade']))
        preco_unit = Decimal(str(item_data['preco_unitario']))
        desconto_item = Decimal(str(item_data.get('desconto', '0')))

        # Calcula comissão do vendedor
        comissao_pct = Decimal('0')
        try:
            comissao_pct = venda.vendedor.comissao_percentual
        except Exception:
            pass

        item = ItemVenda.objects.create(
            venda=venda, produto=produto, grade=grade,
            quantidade=quantidade, preco_unitario=preco_unit,
            desconto=desconto_item,
            comissao_percentual=comissao_pct,
        )

        # Baixa estoque
        alvo = grade if grade else produto
        saldo_ant = alvo.estoque_atual
        novo_saldo = max(Decimal('0'), saldo_ant - quantidade)
        alvo.estoque_atual = novo_saldo
        alvo.save(update_fields=['estoque_atual'])

        MovimentacaoEstoque.objects.create(
            produto=produto, grade=grade,
            tipo='SAIDA_VENDA', quantidade=quantidade,
            saldo_anterior=saldo_ant, saldo_atual=novo_saldo,
            referencia_id=venda.pk, referencia_tipo='Venda',
            usuario=request.user,
        )

    # Recalcula totais da venda
    venda.recalcular_totais()

    # Registra pagamentos
    total_pago = Decimal('0')
    for pag in pagamentos_data:
        valor_pag = Decimal(str(pag['valor']))
        PagamentoVenda.objects.create(
            venda=venda,
            forma=pag['forma'],
            valor=valor_pag,
            parcelas=pag.get('parcelas', 1),
            nsu=pag.get('nsu', ''),
        )
        total_pago += valor_pag

        # Registra no caixa
        if sessao_caixa and pag['forma'] == 'DINHEIRO':
            MovimentacaoCaixa.objects.create(
                sessao=sessao_caixa, tipo='VENDA',
                valor=valor_pag,
                descricao=f'Venda {venda.numero}',
                referencia=venda.numero,
                usuario=request.user,
            )
            sessao_caixa.total_dinheiro += valor_pag
            sessao_caixa.save(update_fields=['total_dinheiro'])

    # Atualiza status de pagamento
    venda.valor_pago = total_pago
    venda.valor_troco = max(Decimal('0'), total_pago - venda.valor_total)
    if total_pago >= venda.valor_total:
        venda.status = 'PAGO'
    elif total_pago > 0:
        venda.status = 'PARCIAL'
    venda.save()

    # Gera contas a receber se crediário/carnê
    for pag in pagamentos_data:
        if pag['forma'] in ('CREDIARIO', 'CARNE') and venda.cliente:
            _gerar_carne_ou_crediario(venda, pag, request.user)

    # Atualiza saldo do cliente
    if venda.cliente:
        _atualizar_saldo_cliente(venda.cliente)

    return JsonResponse({
        'ok': True,
        'venda_id': venda.pk,
        'numero': venda.numero,
        'troco': str(venda.valor_troco),
        'mensagem': f'Venda {venda.numero} finalizada!',
    })


@login_required
def detalhe(request, pk):
    venda = get_object_or_404(
        Venda.objects.select_related('cliente', 'vendedor', 'usuario', 'caixa'), pk=pk
    )
    itens = venda.itens.select_related('produto', 'grade__cor', 'grade__tamanho').all()
    pagamentos = venda.pagamentos.all()

    return render(request, 'vendas/detalhe.html', {
        'titulo': f'Venda {venda.numero}',
        'venda': venda, 'itens': itens, 'pagamentos': pagamentos,
    })


@login_required
def cancelar(request, pk):
    venda = get_object_or_404(Venda, pk=pk)

    if venda.status == 'CANCELADO':
        messages.warning(request, 'Venda já está cancelada.')
        return redirect('vendas:detalhe', pk=pk)

    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        if not motivo:
            messages.error(request, 'Informe o motivo do cancelamento.')
            return redirect('vendas:detalhe', pk=pk)

        # Repõe estoque
        from apps.estoque.models import MovimentacaoEstoque
        for item in venda.itens.select_related('produto', 'grade').all():
            alvo = item.grade if item.grade else item.produto
            saldo_ant = alvo.estoque_atual
            alvo.estoque_atual += item.quantidade
            alvo.save(update_fields=['estoque_atual'])
            MovimentacaoEstoque.objects.create(
                produto=item.produto, grade=item.grade,
                tipo='ENTRADA_DEVOLUCAO', quantidade=item.quantidade,
                saldo_anterior=saldo_ant, saldo_atual=alvo.estoque_atual,
                referencia_id=venda.pk, referencia_tipo='CancelamentoVenda',
                usuario=request.user,
            )

        venda.status = 'CANCELADO'
        venda.cancelado_por = request.user
        venda.motivo_cancelamento = motivo
        venda.save()

        messages.success(request, f'Venda {venda.numero} cancelada. Estoque reposto.')
        return redirect('vendas:lista')

    return render(request, 'vendas/cancelar.html', {
        'titulo': f'Cancelar Venda {venda.numero}', 'venda': venda,
    })


@login_required
def cupom(request, pk):
    """Impressão do cupom de venda."""
    venda = get_object_or_404(Venda.objects.select_related('cliente'), pk=pk)
    itens = venda.itens.select_related('produto').all()
    pagamentos = venda.pagamentos.all()
    try:
        from apps.configuracoes.models import ConfiguracaoLoja
        config = ConfiguracaoLoja.get_config()
    except Exception:
        config = None

    return render(request, 'vendas/cupom.html', {
        'venda': venda, 'itens': itens, 'pagamentos': pagamentos, 'config': config,
    })


# ---- Auxiliares ----

def _gerar_carne_ou_crediario(venda, pag_data, usuario):
    """Gera carnê automaticamente para vendas a prazo."""
    from apps.carne.models import Carne
    parcelas = int(pag_data.get('parcelas', 1))
    valor = Decimal(str(pag_data['valor']))

    if parcelas < 2:
        return

    dia_venc = venda.cliente.dia_vencimento or 10
    carne = Carne.objects.create(
        numero=gerar_numero_sequencial(Carne, 'numero', 'CR', 6),
        cliente=venda.cliente,
        venda=venda,
        valor_total=valor,
        quantidade_parcelas=parcelas,
        valor_parcela=(valor / parcelas).quantize(Decimal('0.01')),
        dia_vencimento=dia_venc,
        usuario=usuario,
    )
    carne.gerar_parcelas()


def _atualizar_saldo_cliente(cliente):
    from apps.financeiro.models import ContaReceber
    total = ContaReceber.objects.filter(
        cliente=cliente, status__in=['PENDENTE', 'PARCIAL', 'VENCIDO']
    ).aggregate(t=Sum('valor_pendente'))['t'] or 0
    cliente.saldo_devedor = total
    cliente.save(update_fields=['saldo_devedor'])
