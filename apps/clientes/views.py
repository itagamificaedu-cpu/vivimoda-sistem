from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Cliente
from .forms import FormCliente


@login_required
def lista(request):
    qs = Cliente.objects.all()
    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    ativo = request.GET.get('ativo', '1')

    if q:
        qs = qs.filter(
            Q(nome__icontains=q) | Q(cpf__icontains=q) |
            Q(celular__icontains=q) | Q(cnpj__icontains=q)
        )
    if categoria:
        qs = qs.filter(categoria=categoria)
    if ativo in ('1', '0'):
        qs = qs.filter(ativo=(ativo == '1'))

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'clientes/lista.html', {
        'titulo': 'Clientes', 'page_obj': page,
        'q': q, 'categoria': categoria, 'ativo': ativo,
        'categorias': Cliente.CATEGORIAS, 'total': qs.count(),
    })


@login_required
def detalhe(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    # Histórico de compras
    vendas = []
    try:
        vendas = cliente.venda_set.select_related().order_by('-data_venda')[:20]
    except Exception:
        pass

    return render(request, 'clientes/detalhe.html', {
        'titulo': cliente.nome, 'cliente': cliente, 'vendas': vendas,
    })


@login_required
def criar(request):
    if request.method == 'POST':
        form = FormCliente(request.POST, request.FILES)
        if form.is_valid():
            c = form.save()
            messages.success(request, f'Cliente {c.nome} cadastrado!')
            return redirect('clientes:detalhe', pk=c.pk)
    else:
        form = FormCliente()
    return render(request, 'clientes/form.html', {'titulo': 'Novo Cliente', 'form': form})


@login_required
def editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = FormCliente(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado!')
            return redirect('clientes:detalhe', pk=pk)
    else:
        form = FormCliente(instance=cliente)
    return render(request, 'clientes/form.html', {
        'titulo': f'Editar — {cliente.nome}', 'form': form, 'cliente': cliente,
    })


@login_required
def excluir(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.ativo = False
        cliente.save()
        messages.success(request, f'{cliente.nome} desativado.')
        return redirect('clientes:lista')
    return redirect('clientes:detalhe', pk=pk)


@login_required
def buscar_ajax(request):
    """Endpoint para Select2 no PDV e formulários."""
    q = request.GET.get('q', '')
    clientes = Cliente.objects.filter(
        Q(nome__icontains=q) | Q(cpf__icontains=q) | Q(celular__icontains=q),
        ativo=True
    )[:20]
    return JsonResponse({
        'results': [
            {'id': c.pk, 'text': f'{c.nome} — {c.celular}', 'nome': c.nome,
             'celular': c.celular, 'saldo': str(c.saldo_devedor)}
            for c in clientes
        ]
    })
