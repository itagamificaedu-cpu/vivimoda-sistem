from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Fornecedor, ContatoFornecedor, AnexoFornecedor
from .forms import FormFornecedor, FormContatoFornecedor


@login_required
def lista(request):
    qs = Fornecedor.objects.all()
    q = request.GET.get('q', '')
    ativo = request.GET.get('ativo', '1')

    if q:
        qs = qs.filter(
            Q(razao_social__icontains=q) | Q(nome_fantasia__icontains=q) |
            Q(cnpj__icontains=q)
        )
    if ativo in ('1', '0'):
        qs = qs.filter(ativo=(ativo == '1'))

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'fornecedores/lista.html', {
        'titulo': 'Fornecedores', 'page_obj': page,
        'q': q, 'ativo': ativo, 'total': qs.count(),
    })


@login_required
def detalhe(request, pk):
    forn = get_object_or_404(Fornecedor, pk=pk)
    compras = []
    try:
        compras = forn.ordemcompra_set.order_by('-criado_em')[:10]
    except Exception:
        pass
    return render(request, 'fornecedores/detalhe.html', {
        'titulo': str(forn), 'fornecedor': forn, 'compras': compras,
    })


@login_required
def criar(request):
    if request.method == 'POST':
        form = FormFornecedor(request.POST)
        if form.is_valid():
            f = form.save()
            messages.success(request, f'Fornecedor {f} cadastrado!')
            return redirect('fornecedores:detalhe', pk=f.pk)
    else:
        form = FormFornecedor()
    return render(request, 'fornecedores/form.html', {'titulo': 'Novo Fornecedor', 'form': form})


@login_required
def editar(request, pk):
    forn = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        form = FormFornecedor(request.POST, instance=forn)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor atualizado!')
            return redirect('fornecedores:detalhe', pk=pk)
    else:
        form = FormFornecedor(instance=forn)
    return render(request, 'fornecedores/form.html', {
        'titulo': f'Editar — {forn}', 'form': form, 'fornecedor': forn,
    })


@login_required
def excluir(request, pk):
    forn = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        forn.ativo = False
        forn.save()
        messages.success(request, f'{forn} desativado.')
        return redirect('fornecedores:lista')
    return redirect('fornecedores:detalhe', pk=pk)


@login_required
def buscar_ajax(request):
    q = request.GET.get('q', '')
    forn = Fornecedor.objects.filter(
        Q(razao_social__icontains=q) | Q(nome_fantasia__icontains=q),
        ativo=True
    )[:20]
    return JsonResponse({
        'results': [{'id': f.pk, 'text': str(f)} for f in forn]
    })
