"""
Mixins reutilizáveis para views e models do ConfecSystem.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings


class LoginObrigatorioMixin(LoginRequiredMixin):
    """Redireciona para login se não autenticado."""
    login_url = '/auth/login/'

    def handle_no_permission(self):
        messages.warning(self.request, 'Você precisa estar logado para acessar essa página.')
        return redirect(self.login_url)


class PermissaoPerfilMixin(LoginObrigatorioMixin, UserPassesTestMixin):
    """
    Verifica se o usuário tem o perfil necessário.
    Defina `perfis_permitidos = ['master', 'gerente']` na view.
    """
    perfis_permitidos = []

    def test_func(self):
        usuario = self.request.user
        if not hasattr(usuario, 'perfil'):
            return False
        return usuario.perfil.cargo in self.perfis_permitidos or usuario.perfil.cargo == 'master'

    def handle_no_permission(self):
        messages.error(self.request, 'Você não tem permissão para acessar essa área.')
        return redirect('core:dashboard')


class AjaxMixin:
    """Métodos auxiliares para views que respondem a requisições AJAX."""

    def json_sucesso(self, dados=None, mensagem='Operação realizada com sucesso.'):
        return JsonResponse({'ok': True, 'mensagem': mensagem, 'dados': dados or {}})

    def json_erro(self, mensagem='Ocorreu um erro.', erros=None, status=400):
        return JsonResponse({'ok': False, 'mensagem': mensagem, 'erros': erros or {}}, status=status)


class ListagemMixin:
    """
    Adiciona paginação e filtros persistentes na sessão para listagens.
    """
    paginate_by = settings.LISTAGEM_ITENS_POR_PAGINA

    def get_paginate_by(self, queryset):
        # Permite que o usuário mude itens por página via GET
        return self.request.GET.get('por_pagina', self.paginate_by)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_itens'] = self.get_queryset().count()
        return ctx


class SalvarUsuarioMixin:
    """Salva automaticamente o usuário logado ao criar/editar registros."""

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class MensagemSucessoMixin:
    """Adiciona mensagem de sucesso automática após salvar."""
    mensagem_criado = 'Registro criado com sucesso!'
    mensagem_atualizado = 'Registro atualizado com sucesso!'
    mensagem_excluido = 'Registro excluído com sucesso!'

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object._state.adding:
            messages.success(self.request, self.mensagem_criado)
        else:
            messages.success(self.request, self.mensagem_atualizado)
        return response
