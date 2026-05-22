"""
Views de autenticação: login, logout, perfil, usuários, logs.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.views.generic import ListView

from apps.core.mixins import LoginObrigatorioMixin, PermissaoPerfilMixin
from .models import Usuario, PerfilUsuario, LogAcesso, TentativaLogin
from .forms import FormLogin, FormTrocarSenha, FormPerfilUsuario, FormCriarUsuario


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def view_login(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = FormLogin(request, data=request.POST)
        username = request.POST.get('username', '')
        ip = _get_ip(request)

        # Verifica bloqueio por tentativas
        tentativa, _ = TentativaLogin.objects.get_or_create(
            username=username, ip=ip,
            defaults={'tentativas': 0}
        )
        if tentativa.esta_bloqueado():
            messages.error(request, f'Usuário bloqueado por excesso de tentativas. Aguarde {settings.BLOQUEIO_LOGIN_MINUTOS} minutos.')
            return render(request, 'autenticacao/login.html', {'form': form})

        if form.is_valid():
            user = form.get_user()
            tentativa.resetar()
            login(request, user)
            LogAcesso.objects.create(
                usuario=user, acao='LOGIN', ip=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            messages.success(request, f'Bem-vindo, {user.nome_exibicao}!')
            return redirect(request.GET.get('next', 'core:dashboard'))
        else:
            tentativa.registrar_falha(
                max_tentativas=settings.TENTATIVAS_LOGIN_MAX,
                minutos_bloqueio=settings.BLOQUEIO_LOGIN_MINUTOS
            )
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = FormLogin(request)

    return render(request, 'autenticacao/login.html', {'form': form})


@login_required
def view_logout(request):
    LogAcesso.objects.create(
        usuario=request.user, acao='LOGOUT', ip=_get_ip(request)
    )
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('autenticacao:login')


@login_required
def view_perfil(request):
    usuario = request.user
    perfil = getattr(usuario, 'perfil', None)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'trocar_senha':
            form_senha = FormTrocarSenha(usuario, request.POST)
            if form_senha.is_valid():
                form_senha.save()
                messages.success(request, 'Senha alterada com sucesso! Faça login novamente.')
                return redirect('autenticacao:login')
            else:
                messages.error(request, 'Erro ao alterar senha. Verifique os campos.')
        elif action == 'atualizar_foto' and perfil:
            form_perfil = FormPerfilUsuario(request.POST, request.FILES, instance=perfil)
            if form_perfil.is_valid():
                form_perfil.save()
                messages.success(request, 'Foto atualizada.')
                return redirect('autenticacao:perfil')

    ctx = {
        'titulo': 'Meu Perfil',
        'form_senha': FormTrocarSenha(usuario),
        'perfil': perfil,
    }
    return render(request, 'autenticacao/perfil.html', ctx)


@login_required
def view_usuarios(request):
    if not request.user.perfil.cargo in ('master', 'gerente'):
        messages.error(request, 'Sem permissão.')
        return redirect('core:dashboard')

    usuarios = Usuario.objects.select_related('perfil').order_by('first_name')
    ctx = {
        'titulo': 'Usuários do Sistema',
        'usuarios': usuarios,
    }
    return render(request, 'autenticacao/usuarios.html', ctx)


@login_required
def view_criar_usuario(request):
    if not request.user.perfil.cargo == 'master':
        messages.error(request, 'Apenas o master pode criar usuários.')
        return redirect('autenticacao:usuarios')

    if request.method == 'POST':
        form = FormCriarUsuario(request.POST)
        form_perfil = FormPerfilUsuario(request.POST, request.FILES)
        if form.is_valid() and form_perfil.is_valid():
            usuario = form.save()
            perfil = form_perfil.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            messages.success(request, f'Usuário {usuario.username} criado com sucesso!')
            return redirect('autenticacao:usuarios')
    else:
        form = FormCriarUsuario()
        form_perfil = FormPerfilUsuario()

    return render(request, 'autenticacao/form_usuario.html', {
        'titulo': 'Novo Usuário',
        'form': form,
        'form_perfil': form_perfil,
    })


@login_required
def view_logs(request):
    if not request.user.perfil.cargo in ('master', 'gerente'):
        messages.error(request, 'Sem permissão.')
        return redirect('core:dashboard')

    logs = LogAcesso.objects.select_related('usuario').order_by('-criado_em')[:500]
    return render(request, 'autenticacao/logs.html', {
        'titulo': 'Log de Acessos',
        'logs': logs,
    })


@login_required
def salvar_perfil(request):
    """Salva alterações de dados pessoais do usuário logado."""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save(update_fields=['first_name', 'last_name', 'email'])
        messages.success(request, 'Dados atualizados com sucesso!')
    return redirect('autenticacao:perfil')


@login_required
def alterar_senha(request):
    """Altera senha do usuário logado."""
    if request.method == 'POST':
        from django.contrib.auth import authenticate, update_session_auth_hash
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar = request.POST.get('confirmar_senha')

        user = authenticate(username=request.user.username, password=senha_atual)
        if not user:
            messages.error(request, 'Senha atual incorreta.')
        elif nova_senha != confirmar:
            messages.error(request, 'As novas senhas não conferem.')
        elif len(nova_senha) < 8:
            messages.error(request, 'A nova senha deve ter pelo menos 8 caracteres.')
        else:
            request.user.set_password(nova_senha)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso!')
    return redirect('autenticacao:perfil')


@login_required
def view_editar_usuario(request, pk):
    """Edita um usuário do sistema."""
    usuario = get_object_or_404(Usuario, pk=pk)
    perfil = getattr(usuario, 'perfil', None)

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name', usuario.first_name)
        usuario.last_name = request.POST.get('last_name', usuario.last_name)
        usuario.email = request.POST.get('email', usuario.email)
        usuario.is_active = 'is_active' in request.POST
        usuario.save()

        cargo = request.POST.get('cargo', 'caixa')
        if perfil:
            perfil.cargo = cargo
            perfil.save(update_fields=['cargo'])
        else:
            PerfilUsuario.objects.create(usuario=usuario, cargo=cargo)

        messages.success(request, f'Usuário {usuario.username} atualizado!')
        return redirect('autenticacao:usuarios')

    return render(request, 'autenticacao/form_usuario.html', {
        'titulo': f'Editar Usuário — {usuario.username}',
        'usuario': usuario,
        'perfil': perfil,
    })
