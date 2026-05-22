from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilUsuario, LogAcesso, TentativaLogin


class PerfilInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ['username', 'get_full_name', 'email', 'is_active', 'last_login']
    list_filter = ['is_active', 'is_staff', 'perfil__cargo']


@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'acao', 'modelo', 'ip', 'criado_em']
    list_filter = ['acao', 'criado_em']
    search_fields = ['usuario__username', 'descricao']
    readonly_fields = ['usuario', 'acao', 'modelo', 'objeto_id', 'ip', 'criado_em']
    ordering = ['-criado_em']


@admin.register(TentativaLogin)
class TentativaLoginAdmin(admin.ModelAdmin):
    list_display = ['username', 'ip', 'tentativas', 'bloqueado_ate', 'ultima_tentativa']
    list_filter = ['ultima_tentativa']
