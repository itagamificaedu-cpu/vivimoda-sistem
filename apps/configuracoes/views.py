from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ConfiguracaoLoja
from .forms import FormConfiguracaoLoja


@login_required
def view_configuracoes(request):
    if request.user.perfil.cargo != 'master':
        messages.error(request, 'Apenas o master pode acessar as configurações.')
        return redirect('core:dashboard')

    config = ConfiguracaoLoja.get_config()

    if request.method == 'POST':
        form = FormConfiguracaoLoja(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('configuracoes:index')
    else:
        form = FormConfiguracaoLoja(instance=config)

    return render(request, 'configuracoes/index.html', {
        'titulo': 'Configurações do Sistema',
        'form': form,
        'config': config,
    })
