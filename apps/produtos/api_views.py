"""
Views AJAX de Produtos — retornam JSON para o frontend.
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Produto, GradeProduto


@login_required
def buscar_produto(request):
    """
    GET /api/produtos/buscar/?q=<termo>
    Retorna lista de produtos ativos (máx. 20) para auto-complete.
    Busca por código, código de barras ou nome.
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    qs = Produto.objects.filter(ativo=True).filter(
        Q(codigo__icontains=q) |
        Q(codigo_barras__icontains=q) |
        Q(nome__icontains=q)
    ).select_related('categoria')[:20]

    results = []
    for p in qs:
        results.append({
            'id': p.pk,
            'codigo': p.codigo,
            'nome': p.nome,
            'preco': float(p.preco_vigente),
            'estoque': float(p.estoque_atual),
            'tipo': p.tipo,
            'unidade': p.unidade,
        })

    return JsonResponse({'results': results})


@login_required
def detalhe_produto(request, pk):
    """
    GET /api/produtos/<pk>/
    Retorna detalhe de um produto com grades (se GRADE).
    """
    try:
        p = Produto.objects.select_related('categoria', 'marca').get(pk=pk, ativo=True)
    except Produto.DoesNotExist:
        return JsonResponse({'erro': 'Produto não encontrado'}, status=404)

    dados = {
        'id': p.pk,
        'codigo': p.codigo,
        'nome': p.nome,
        'tipo': p.tipo,
        'preco': float(p.preco_vigente),
        'em_promocao': p.em_promocao,
        'estoque': float(p.estoque_atual),
        'unidade': p.unidade,
        'grades': [],
    }

    if p.tipo == 'GRADE':
        grades = GradeProduto.objects.filter(
            produto=p, ativo=True
        ).select_related('cor', 'tamanho')
        dados['grades'] = [
            {
                'id': g.pk,
                'cor': g.cor.nome,
                'tamanho': g.tamanho.nome,
                'preco': float(g.preco_final),
                'estoque': float(g.estoque_atual),
            }
            for g in grades
        ]

    return JsonResponse(dados)
