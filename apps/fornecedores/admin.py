"""
Admin de Fornecedores.
"""
from django.contrib import admin
from .models import Fornecedor, ContatoFornecedor, AnexoFornecedor


class ContatoInline(admin.TabularInline):
    model = ContatoFornecedor
    extra = 1
    fields = ['nome', 'cargo', 'celular', 'email', 'principal']


class AnexoInline(admin.TabularInline):
    model = AnexoFornecedor
    extra = 0
    fields = ['descricao', 'arquivo', 'criado_em']
    readonly_fields = ['criado_em']


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = [
        'razao_social', 'nome_fantasia', 'cnpj', 'telefone',
        'cidade', 'avaliacao', 'prazo_pagamento', 'ativo',
    ]
    list_filter = ['ativo', 'tipo', 'estado', 'avaliacao']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj', 'cpf', 'email']
    ordering = ['razao_social']
    inlines = [ContatoInline, AnexoInline]
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Identificação', {
            'fields': ('tipo', 'razao_social', 'nome_fantasia', 'cnpj', 'cpf', 'inscricao_estadual')
        }),
        ('Contato', {
            'fields': ('telefone', 'celular', 'email', 'site')
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Condições Comerciais', {
            'fields': ('prazo_pagamento', 'condicao_pagamento', 'desconto_padrao', 'avaliacao')
        }),
        ('Sistema', {
            'fields': ('ativo', 'observacoes', 'criado_em', 'atualizado_em')
        }),
    )
