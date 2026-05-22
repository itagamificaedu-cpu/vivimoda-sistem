from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone

from .models import MovimentacaoEstoque, Inventario, ItemInventario
from apps.produtos.models import Produto, GradeProduto


@login_required
def index(request):
    """Posição atual do estoque."""
    qs = Produto.objects.filter(ativo=True).select_related('categoria')
    q = request.GET.get('q', '')
    filtro = request.GET.get('filtro', '')

    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(codigo__icontains=q))
    if filtro == 'abaixo_minimo':
        qs = qs.filter(tipo='SIMPLES', estoque_atual__lte=F('estoque_minimo'))
    if filtro == 'zerado':
        qs = qs.filter(tipo='SIMPLES', estoque_atual__lte=0)

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    # Métricas do topo
    total_produtos = Produto.objects.filter(ativo=True).count()
    estoque_baixo = Produto.objects.filter(
        ativo=True, tipo='SIMPLES', estoque_atual__lte=F('estoque_minimo')
    ).count()

    return render(request, 'estoque/index.html', {
        'titulo': 'Controle de Estoque',
        'page_obj': page,
        'q': q, 'filtro': filtro,
        'total_produtos': total_produtos,
        'estoque_baixo': estoque_baixo,
    })


@login_required
def movimentacoes(request):
    qs = MovimentacaoEstoque.objects.select_related('produto', 'usuario').all()
    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')

    if q:
        qs = qs.filter(Q(produto__nome__icontains=q) | Q(produto__codigo__icontains=q))
    if tipo:
        qs = qs.filter(tipo=tipo)

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'estoque/movimentacoes.html', {
        'titulo': 'Movimentações de Estoque',
        'page_obj': page, 'q': q, 'tipo': tipo,
        'tipos': MovimentacaoEstoque.TIPOS,
    })


@login_required
def ajuste_manual(request):
    """Ajuste manual de estoque com justificativa obrigatória."""
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        grade_id = request.POST.get('grade_id') or None
        tipo = request.POST.get('tipo')
        quantidade = float(request.POST.get('quantidade', 0))
        observacao = request.POST.get('observacao', '').strip()

        if not observacao:
            messages.error(request, 'Justificativa obrigatória para ajuste manual.')
            return redirect('estoque:ajuste')

        produto = get_object_or_404(Produto, pk=produto_id)
        grade = GradeProduto.objects.filter(pk=grade_id).first() if grade_id else None

        saldo_anterior = grade.estoque_atual if grade else produto.estoque_atual

        if tipo == 'ENTRADA_AJUSTE':
            novo_saldo = saldo_anterior + quantidade
        else:
            novo_saldo = max(0, saldo_anterior - quantidade)

        if grade:
            grade.estoque_atual = novo_saldo
            grade.save(update_fields=['estoque_atual'])
        else:
            produto.estoque_atual = novo_saldo
            produto.save(update_fields=['estoque_atual'])

        MovimentacaoEstoque.objects.create(
            produto=produto, grade=grade,
            tipo=tipo, quantidade=quantidade,
            saldo_anterior=saldo_anterior, saldo_atual=novo_saldo,
            observacao=observacao, usuario=request.user,
        )

        messages.success(request, f'Estoque de "{produto.nome}" ajustado para {novo_saldo}.')
        return redirect('estoque:index')

    produtos = Produto.objects.filter(ativo=True).order_by('nome')
    return render(request, 'estoque/ajuste.html', {
        'titulo': 'Ajuste Manual de Estoque',
        'produtos': produtos,
    })


@login_required
def inventario_lista(request):
    invs = Inventario.objects.select_related('usuario_responsavel').all()
    paginator = Paginator(invs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'estoque/inventario_lista.html', {
        'titulo': 'Inventários', 'page_obj': page,
    })


@login_required
def inventario_novo(request):
    if request.method == 'POST':
        inv = Inventario.objects.create(
            descricao=request.POST.get('descricao', 'Inventário'),
            status='EM_ANDAMENTO',
            usuario_responsavel=request.user,
        )
        # Cria itens para todos os produtos ativos
        for p in Produto.objects.filter(ativo=True):
            ItemInventario.objects.create(
                inventario=inv, produto=p, estoque_sistema=p.estoque_atual,
            )
        messages.success(request, f'Inventário {inv.pk} iniciado!')
        return redirect('estoque:inventario_detalhe', pk=inv.pk)

    return render(request, 'estoque/inventario_novo.html', {'titulo': 'Novo Inventário'})


@login_required
def inventario_detalhe(request, pk):
    inv = get_object_or_404(Inventario, pk=pk)
    itens = inv.itens.select_related('produto').all()
    return render(request, 'estoque/inventario_detalhe.html', {
        'titulo': f'Inventário #{inv.pk}', 'inventario': inv, 'itens': itens,
    })


@login_required
def inventario_salvar(request, pk):
    """Salva contagem física das quantidades no inventário."""
    inv = get_object_or_404(Inventario, pk=pk, status='EM_ANDAMENTO')
    if request.method == 'POST':
        for item in inv.itens.all():
            qtd_str = request.POST.get(f'qtd_{item.pk}', '')
            if qtd_str != '':
                try:
                    contado = float(qtd_str)
                    item.estoque_contado = contado
                    item.divergencia = contado - float(item.estoque_sistema)
                    item.save(update_fields=['estoque_contado', 'divergencia'])
                except ValueError:
                    pass
        messages.success(request, 'Contagem salva com sucesso!')
    return redirect('estoque:inventario_detalhe', pk=pk)


@login_required
def inventario_finalizar(request, pk):
    """Finaliza inventário aplicando ajustes de estoque para itens com divergência."""
    inv = get_object_or_404(Inventario, pk=pk, status='EM_ANDAMENTO')
    if request.method == 'POST':
        for item in inv.itens.all():
            if item.estoque_contado is not None and item.divergencia and item.divergencia != 0:
                produto = item.produto
                saldo_ant = produto.estoque_atual
                saldo_novo = item.estoque_contado

                # Define tipo da movimentação: ajuste de entrada ou saída
                if item.divergencia > 0:
                    tipo_mov = 'ENTRADA_AJUSTE'
                    qtd_mov = float(item.divergencia)
                else:
                    tipo_mov = 'SAIDA_AJUSTE'
                    qtd_mov = abs(float(item.divergencia))

                produto.estoque_atual = saldo_novo
                produto.save(update_fields=['estoque_atual'])

                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo=tipo_mov,
                    quantidade=qtd_mov,
                    saldo_anterior=saldo_ant,
                    saldo_atual=saldo_novo,
                    observacao=f'Ajuste de inventário #{inv.pk}',
                    usuario=request.user,
                )

                item.ajustado = True
                item.save(update_fields=['ajustado'])

        inv.status = 'CONCLUIDO'
        inv.data_fim = timezone.now()
        inv.save(update_fields=['status', 'data_fim'])
        messages.success(request, f'Inventário #{inv.pk} finalizado! Ajustes de estoque aplicados.')
    return redirect('estoque:inventario_detalhe', pk=pk)
