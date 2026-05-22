from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator

from .models import Funcionario, HistoricoSalario, FeriasFuncionario
from .forms import FormFuncionario, FormFerias


@login_required
def lista(request):
    qs = Funcionario.objects.all()
    q = request.GET.get('q', '')
    ativo = request.GET.get('ativo', '')
    cargo = request.GET.get('cargo', '')

    if q:
        qs = qs.filter(Q(nome_completo__icontains=q) | Q(cpf__icontains=q) | Q(celular__icontains=q))
    if ativo in ('1', '0'):
        qs = qs.filter(ativo=(ativo == '1'))
    if cargo:
        qs = qs.filter(cargo__icontains=cargo)

    paginator = Paginator(qs, settings.LISTAGEM_ITENS_POR_PAGINA)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'funcionarios/lista.html', {
        'titulo': 'Funcionários', 'page_obj': page,
        'q': q, 'ativo': ativo, 'cargo': cargo,
        'total': qs.count(),
    })


@login_required
def detalhe(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    return render(request, 'funcionarios/detalhe.html', {
        'titulo': func.nome_completo, 'funcionario': func,
        'historico_salarios': func.historico_salarios.all()[:10],
        'ferias': func.ferias.all()[:10],
    })


@login_required
def criar(request):
    if request.method == 'POST':
        form = FormFuncionario(request.POST, request.FILES)
        if form.is_valid():
            func = form.save()
            messages.success(request, f'Funcionário {func.nome_completo} cadastrado!')
            return redirect('funcionarios:detalhe', pk=func.pk)
    else:
        form = FormFuncionario()
    return render(request, 'funcionarios/form.html', {'titulo': 'Novo Funcionário', 'form': form})


@login_required
def editar(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    salario_anterior = func.salario

    if request.method == 'POST':
        form = FormFuncionario(request.POST, request.FILES, instance=func)
        if form.is_valid():
            novo_salario = form.cleaned_data['salario']
            if novo_salario != salario_anterior:
                HistoricoSalario.objects.create(
                    funcionario=func,
                    salario_anterior=salario_anterior,
                    salario_novo=novo_salario,
                    motivo=request.POST.get('motivo_salario', ''),
                    usuario=request.user,
                )
            form.save()
            messages.success(request, 'Funcionário atualizado!')
            return redirect('funcionarios:detalhe', pk=func.pk)
    else:
        form = FormFuncionario(instance=func)

    return render(request, 'funcionarios/form.html', {
        'titulo': f'Editar — {func.nome_completo}', 'form': form, 'funcionario': func,
    })


@login_required
def excluir(request, pk):
    func = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        func.ativo = False
        func.save()
        messages.success(request, f'{func.nome_completo} desativado.')
        return redirect('funcionarios:lista')
    return redirect('funcionarios:detalhe', pk=pk)
