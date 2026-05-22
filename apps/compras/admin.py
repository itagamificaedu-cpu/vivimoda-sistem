"""
Admin de Compras — Ordens de Compra.
"""
from django.contrib import admin
from .models import OrdemCompra, ItemOrdemCompra


class ItemOrdemCompraInline(admin.TabularInline):
    model = ItemOrdemCompra
    extra = 1
    fields = [
        'produto', 'grade', 'quantidade_pedida', 'quantidade_recebida',
        'preco_unitario', 'desconto', 'valor_total',
    ]
    readonly_fields = ['valor_total']


@admin.register(OrdemCompra)
class OrdemCompraAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'fornecedor', 'data_pedido', 'data_previsao',
        'valor_total', 'status', 'usuario',
    ]
    list_filter = ['status', 'data_pedido', 'fornecedor']
    search_fields = ['numero', 'fornecedor__razao_social', 'nf_numero']
    ordering = ['-criado_em']
    readonly_fields = [
        'numero', 'valor_produtos', 'valor_total',
        'data_pedido', 'criado_em', 'atualizado_em', 'usuario',
    ]
    inlines = [ItemOrdemCompraInline]
    date_hierarchy = 'data_pedido'
    fieldsets = (
        ('Identificação', {
            'fields': ('numero', 'fornecedor', 'status', 'condicao_pagamento')
        }),
        ('Datas', {
            'fields': ('data_pedido', 'data_previsao', 'data_recebimento')
        }),
        ('Valores', {
            'fields': ('valor_produtos', 'valor_frete', 'valor_desconto', 'valor_total')
        }),
        ('Nota Fiscal', {
            'fields': ('nf_numero', 'nf_arquivo'),
            'classes': ('collapse',),
        }),
        ('Sistema', {
            'fields': ('usuario', 'observacoes', 'criado_em', 'atualizado_em')
        }),
    )
