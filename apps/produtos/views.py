"""
Views do módulo Produtos: CRUD, busca AJAX para PDV, etiquetas.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal

from .models import Produto, GradeProduto, Categoria, Marca, Cor, Tamanho, HistoricoPreco
from .forms import FormProduto, FormGrade, FormCategoria


@login_required
def lista(request):
    qs = Produto.objects.select_related('categoria', 'marca').all()
    q = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    ativo = request.GET.get('ativo', '1')
    estoque_baixo = request.GET.get('estoque_baixo', '')

    if q:
        qs = qs.filter(
            Q(nome__icontains=q) | Q(codigo__icontains=q) |
            Q(codigo_barras__icontains=q) | Q(referencia__icontains=q)
        )
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    if ativo in ('1', '0'):
        qs = qs.filter(ativo=(ativo == '1'))
    if estoque_baixo:
        qs = qs.filter(tipo='SIMPLES').filter(
            estoque_atual__lte=models_estoque_minimo()
        )

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'produtos/lista.html', {
        'titulo': 'Produtos',
        'page_obj': page,
        'categorias': Categoria.objects.filter(ativo=True),
        'q': q, 'categoria_id': categoria_id, 'ativo': ativo,
        'total': qs.count(),
    })


def models_estoque_minimo():
    from django.db.models import F
    return F('estoque_minimo')


@login_required
def detalhe(request, pk):
    produto = get_object_or_404(Produto.objects.select_related('categoria', 'marca'), pk=pk)
    grades = produto.grades.select_related('cor', 'tamanho').filter(ativo=True)
    historico = produto.historico_precos.select_related('usuario').all()[:10]

    return render(request, 'produtos/detalhe.html', {
        'titulo': produto.nome,
        'produto': produto,
        'grades': grades,
        'historico': historico,
    })


@login_required
def criar(request):
    if request.method == 'POST':
        form = FormProduto(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            # Gera código automático se não informado
            if not produto.codigo:
                from apps.core.utils import gerar_numero_sequencial
                produto.codigo = gerar_numero_sequencial(Produto, 'codigo', 'PRD', 6)
            preco_anterior = None
            produto.save()
            messages.success(request, f'Produto "{produto.nome}" cadastrado!')
            return redirect('produtos:detalhe', pk=produto.pk)
    else:
        form = FormProduto()
    return render(request, 'produtos/form.html', {'titulo': 'Novo Produto', 'form': form})


@login_required
def editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    preco_anterior = produto.preco_venda

    if request.method == 'POST':
        form = FormProduto(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            novo_preco = form.cleaned_data['preco_venda']
            if novo_preco != preco_anterior:
                HistoricoPreco.objects.create(
                    produto=produto,
                    preco_anterior=preco_anterior,
                    preco_novo=novo_preco,
                    motivo=request.POST.get('motivo_preco', ''),
                    usuario=request.user,
                )
            form.save()
            messages.success(request, 'Produto atualizado!')
            return redirect('produtos:detalhe', pk=pk)
    else:
        form = FormProduto(instance=produto)

    return render(request, 'produtos/form.html', {
        'titulo': f'Editar — {produto.nome}', 'form': form, 'produto': produto,
    })


@login_required
def excluir(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.ativo = False
        produto.save()
        messages.success(request, f'Produto "{produto.nome}" desativado.')
        return redirect('produtos:lista')
    return redirect('produtos:detalhe', pk=pk)


@login_required
def buscar_ajax(request):
    """Busca de produtos para o PDV via AJAX — retorna dados completos."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})

    produtos = Produto.objects.filter(
        Q(nome__icontains=q) | Q(codigo__icontains=q) |
        Q(codigo_barras=q) | Q(codigo_barras__icontains=q),
        ativo=True
    ).select_related('categoria')[:15]

    results = []
    for p in produtos:
        if p.tipo == 'GRADE':
            grades = p.grades.filter(ativo=True).select_related('cor', 'tamanho')
            for g in grades:
                results.append({
                    'id': p.pk,
                    'grade_id': g.pk,
                    'text': f'{p.nome} — {g.cor} / {g.tamanho}',
                    'nome': p.nome,
                    'codigo': p.codigo,
                    'codigo_barras': p.codigo_barras or '',
                    'preco': str(g.preco_final),
                    'estoque': str(g.estoque_atual),
                    'cor': str(g.cor),
                    'tamanho': str(g.tamanho),
                    'tem_grade': True,
                })
        else:
            results.append({
                'id': p.pk,
                'grade_id': None,
                'text': f'{p.codigo} — {p.nome}',
                'nome': p.nome,
                'codigo': p.codigo,
                'codigo_barras': p.codigo_barras or '',
                'preco': str(p.preco_vigente),
                'estoque': str(p.estoque_atual),
                'em_promocao': p.em_promocao,
                'tem_grade': False,
            })

    return JsonResponse({'results': results})


@login_required
def calcular_preco(request):
    """Calcula preço de venda a partir do custo + margem (AJAX)."""
    custo = Decimal(request.GET.get('custo', '0'))
    margem = Decimal(request.GET.get('margem', '0'))
    preco = custo * (1 + margem / 100)
    return JsonResponse({'preco': str(preco.quantize(Decimal('0.01')))})\


@login_required
def lista_categorias(request):
    cats = Categoria.objects.all()
    paginator = Paginator(cats, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'produtos/categorias.html', {
        'titulo': 'Categorias', 'page_obj': page,
    })


@login_required
def salvar_categoria(request):
    if request.method == 'POST':
        form = FormCategoria(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria salva!')
    return redirect('produtos:categorias')
