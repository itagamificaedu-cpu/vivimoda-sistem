"""
Admin de Clientes.
"""
from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'cpf', 'celular', 'cidade', 'categoria',
        'saldo_devedor', 'limite_credito', 'ativo',
    ]
    list_filter = ['ativo', 'categoria', 'tipo', 'estado']
    search_fields = ['nome', 'cpf', 'cnpj', 'celular', 'email']
    ordering = ['nome']
    readonly_fields = ['saldo_devedor', 'pontos_fidelidade', 'criado_em', 'atualizado_em']
    fieldsets = (
        ('Identificação', {
            'fields': ('tipo', 'nome', 'cpf', 'rg', 'data_nascimento', 'sexo',
                       'razao_social', 'cnpj', 'inscricao_estadual', 'nome_fantasia')
        }),
        ('Contato', {
            'fields': ('telefone', 'celular', 'whatsapp', 'email')
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Financeiro', {
            'fields': ('limite_credito', 'saldo_devedor', 'dia_vencimento', 'categoria',
                       'pontos_fidelidade')
        }),
        ('Sistema', {
            'fields': ('foto', 'ativo', 'observacoes', 'criado_em', 'atualizado_em')
        }),
    )
