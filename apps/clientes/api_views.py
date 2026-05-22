"""
Views AJAX de Clientes — retornam JSON para o frontend.
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Cliente


@login_required
def buscar_cliente(request):
    """
    GET /api/clientes/buscar/?q=<termo>
    Retorna lista de clientes ativos (máx. 15) para auto-complete no PDV.
    Busca por nome, CPF ou celular.
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    qs = Cliente.objects.filter(ativo=True).filter(
        Q(nome__icontains=q) |
        Q(cpf__icontains=q) |
        Q(celular__icontains=q)
    )[:15]

    results = [
        {
            'id': c.pk,
            'nome': c.nome,
            'cpf': c.cpf or '',
            'celular': c.celular,
            'limite_credito': float(c.limite_credito),
            'saldo_devedor': float(c.saldo_devedor),
            'categoria': c.categoria,
        }
        for c in qs
    ]

    return JsonResponse({'results': results})


@login_required
def detalhe_cliente(request, pk):
    """
    GET /api/clientes/<pk>/
    Retorna dados financeiros do cliente para exibição no PDV.
    """
    try:
        c = Cliente.objects.get(pk=pk, ativo=True)
    except Cliente.DoesNotExist:
        return JsonResponse({'erro': 'Cliente não encontrado'}, status=404)

    return JsonResponse({
        'id': c.pk,
        'nome': c.nome,
        'cpf': c.cpf or '',
        'celular': c.celular,
        'limite_credito': float(c.limite_credito),
        'saldo_devedor': float(c.saldo_devedor),
        'categoria': c.categoria,
        'inadimplente': c.inadimplente,
    })
