"""
Views AJAX de Estoque.
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.produtos.models import Produto, GradeProduto


@login_required
def saldo_produto(request, produto_pk):
    """
    GET /api/estoque/saldo/<produto_pk>/
    Retorna saldo atual do produto simples.
    """
    try:
        p = Produto.objects.get(pk=produto_pk)
        return JsonResponse({'produto_id': p.pk, 'saldo': float(p.estoque_atual)})
    except Produto.DoesNotExist:
        return JsonResponse({'erro': 'Produto não encontrado'}, status=404)


@login_required
def saldo_grade(request, grade_pk):
    """
    GET /api/estoque/saldo/grade/<grade_pk>/
    Retorna saldo de uma variação de grade.
    """
    try:
        g = GradeProduto.objects.select_related('produto', 'cor', 'tamanho').get(pk=grade_pk)
        return JsonResponse({
            'grade_id': g.pk,
            'produto': g.produto.nome,
            'cor': g.cor.nome,
            'tamanho': g.tamanho.nome,
            'saldo': float(g.estoque_atual),
        })
    except GradeProduto.DoesNotExist:
        return JsonResponse({'erro': 'Grade não encontrada'}, status=404)
