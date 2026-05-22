from django.contrib import admin
from .models import ConfiguracaoLoja


@admin.register(ConfiguracaoLoja)
class ConfiguracaoLojaAdmin(admin.ModelAdmin):
    list_display = ['nome_fantasia', 'cpf_cnpj', 'telefone', 'atualizado_em']
