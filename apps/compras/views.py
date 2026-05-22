from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from .models import OrdemCompra, ItemOrdemCompra
from apps.core.utils import gerar_numero_sequencial
from apps.estoque.models import MovimentacaoEstoque


@login_required
def lista(request):
    qs = OrdemCompra.objects.select_related('fornecedor').all()
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')

    if q:
        qs = qs.filter(Q(numero__icontains=q) | Q(fornecedor__razao_social__icontains=q))
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'compras/lista.html', {
        'titulo': 'Ordens de Compra',
        'page_obj': page, 'q': q, 'status': status,
        'status_choices': OrdemCompra.STATUS,
        'total': qs.count(),
    })


@login_required
def detalhe(request, pk):
    ordem = get_object_or_404(OrdemCompra.objects.select_related('fornecedor', 'usuario'), pk=pk)
    itens = ordem.itens.select_related('produto', 'grade').all()
    return render(request, 'compras/detalhe.html', {
        'titulo': f'OC {ordem.numero}', 'ordem': ordem, 'itens': itens,
    })


@login_required
def criar(request):
    from apps.fornecedores.models import Fornecedor
    from apps.produtos.models import Produto

    if request.method == 'POST':
        fornecedor_id = request.POST.get('fornecedor')
        data_previsao = request.POST.get('data_previsao') or None
        condicao = request.POST.get('condicao_pagamento', '')
        observacoes = request.POST.get('observacoes', '')

        ordem = OrdemCompra.objects.create(
            numero=gerar_numero_sequencial(OrdemCompra, 'numero', 'OC', 6),
            fornecedor_id=fornecedor_id,
            data_previsao=data_previsao,
            condicao_pagamento=condicao,
            observacoes=observacoes,
            usuario=request.user,
        )

        # Adiciona itens do POST
        produtos_ids = request.POST.getlist('produto_id')
        quantidades = request.POST.getlist('quantidade')
        precos = request.POST.getlist('preco_unitario')

        for i, pid in enumerate(produtos_ids):
            if pid and quantidades[i]:
                ItemOrdemCompra.objects.create(
                    ordem=ordem,
                    produto_id=pid,
                    quantidade_pedida=float(quantidades[i]),
                    preco_unitario=float(precos[i]),
                )

        ordem.recalcular_totais()
        messages.success(request, f'Ordem de compra {ordem.numero} criada!')
        return redirect('compras:detalhe', pk=ordem.pk)

    fornecedores = Fornecedor.objects.filter(ativo=True).order_by('razao_social')
    produtos = Produto.objects.filter(ativo=True).order_by('nome')
    return render(request, 'compras/form.html', {
        'titulo': 'Nova Ordem de Compra',
        'fornecedores': fornecedores,
        'produtos': produtos,
    })


@login_required
def editar(request, pk):
    """Edita uma ordem de compra que ainda não foi recebida."""
    from apps.fornecedores.models import Fornecedor
    from apps.produtos.models import Produto

    ordem = get_object_or_404(OrdemCompra, pk=pk)

    if ordem.status in ('RECEBIDA', 'CANCELADA'):
        messages.warning(request, f'Ordem {ordem.numero} não pode ser editada no status atual.')
        return redirect('compras:detalhe', pk=pk)

    if request.method == 'POST':
        ordem.fornecedor_id = request.POST.get('fornecedor') or ordem.fornecedor_id
        ordem.data_previsao = request.POST.get('data_previsao') or None
        ordem.condicao_pagamento = request.POST.get('condicao_pagamento', '')
        ordem.observacoes = request.POST.get('observacoes', '')
        ordem.save()

        # Remove itens antigos e recria
        ordem.itens.all().delete()
        produtos_ids = request.POST.getlist('produto_id')
        quantidades  = request.POST.getlist('quantidade')
        precos       = request.POST.getlist('preco_unitario')
        for i, pid in enumerate(produtos_ids):
            if pid and quantidades[i]:
                ItemOrdemCompra.objects.create(
                    ordem=ordem,
                    produto_id=pid,
                    quantidade_pedida=float(quantidades[i]),
                    preco_unitario=float(precos[i]),
                )

        ordem.recalcular_totais()
        messages.success(request, f'Ordem {ordem.numero} atualizada!')
        return redirect('compras:detalhe', pk=pk)

    fornecedores = Fornecedor.objects.filter(ativo=True).order_by('razao_social')
    produtos = Produto.objects.filter(ativo=True).order_by('nome')
    return render(request, 'compras/form.html', {
        'titulo': f'Editar Ordem {ordem.numero}',
        'ordem': ordem,
        'fornecedores': fornecedores,
        'produtos': produtos,
    })


@login_required
def receber(request, pk):
    """Recebimento parcial ou total da ordem de compra."""
    ordem = get_object_or_404(OrdemCompra, pk=pk)

    if request.method == 'POST':
        itens_ids = request.POST.getlist('item_id')
        qtd_recebidas = request.POST.getlist('qtd_recebida')
        nf_numero = request.POST.get('nf_numero', '')

        for i, item_id in enumerate(itens_ids):
            item = ItemOrdemCompra.objects.get(pk=item_id)
            qtd = float(qtd_recebidas[i] or 0)
            if qtd > 0:
                item.quantidade_recebida += qtd
                item.save()

                # Atualiza estoque
                produto = item.produto
                saldo_ant = item.grade.estoque_atual if item.grade else produto.estoque_atual
                novo_saldo = saldo_ant + qtd

                if item.grade:
                    item.grade.estoque_atual = novo_saldo
                    item.grade.save()
                else:
                    produto.estoque_atual = novo_saldo
                    produto.save(update_fields=['estoque_atual'])

                MovimentacaoEstoque.objects.create(
                    produto=produto, grade=item.grade,
                    tipo='ENTRADA_COMPRA', quantidade=qtd,
                    custo_unitario=item.preco_unitario,
                    saldo_anterior=saldo_ant, saldo_atual=novo_saldo,
                    referencia_id=ordem.pk, referencia_tipo='OrdemCompra',
                    usuario=request.user,
                )

        # Atualiza status da OC
        if nf_numero:
            ordem.nf_numero = nf_numero
        total_pedido = sum(i.quantidade_pedida for i in ordem.itens.all())
        total_recebido = sum(i.quantidade_recebida for i in ordem.itens.all())
        if total_recebido >= total_pedido:
            ordem.status = 'RECEBIDO'
            ordem.data_recebimento = timezone.localdate()
        elif total_recebido > 0:
            ordem.status = 'PARCIAL'
        ordem.save()

        # Gera conta a pagar automaticamente
        _gerar_conta_pagar(ordem, request.user)

        messages.success(request, 'Recebimento registrado e estoque atualizado!')
        return redirect('compras:detalhe', pk=pk)

    itens = ordem.itens.select_related('produto').all()
    return render(request, 'compras/receber.html', {
        'titulo': f'Receber OC {ordem.numero}',
        'ordem': ordem, 'itens': itens,
    })


def _gerar_conta_pagar(ordem, usuario):
    """Gera conta a pagar ao receber mercadoria."""
    from apps.financeiro.models import ContaPagar
    from apps.core.utils import gerar_numero_sequencial
    from datetime import date, timedelta

    if ContaPagar.objects.filter(compra=ordem).exists():
        return  # Já gerou

    prazo = ordem.fornecedor.prazo_pagamento if ordem.fornecedor else 30
    ContaPagar.objects.create(
        numero=gerar_numero_sequencial(ContaPagar, 'numero', 'CP', 6),
        fornecedor=ordem.fornecedor,
        compra=ordem,
        descricao=f'OC {ordem.numero} — {ordem.fornecedor}',
        valor_original=ordem.valor_total,
        valor_pendente=ordem.valor_total,
        data_vencimento=date.today() + timedelta(days=prazo),
        usuario=usuario,
    )
