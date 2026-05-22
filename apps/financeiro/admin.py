"""
Admin Financeiro — Contas a Receber/Pagar, Lançamentos, Contas Bancárias e Plano de Contas.
"""
from django.contrib import admin
from .models import ContaReceber, ContaPagar, LancamentoFinanceiro, ContaBancaria, PlanoContas


@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'cliente', 'descricao', 'valor_original', 'valor_pago',
        'valor_pendente', 'data_vencimento', 'status',
    ]
    list_filter = ['status', 'data_vencimento', 'forma_recebimento']
    search_fields = ['numero', 'cliente__nome', 'descricao']
    ordering = ['data_vencimento']
    readonly_fields = ['numero', 'valor_pendente', 'criado_em']
    date_hierarchy = 'data_vencimento'


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = [
        'numero', 'fornecedor', 'descricao', 'valor_original', 'valor_pago',
        'valor_pendente', 'data_vencimento', 'status',
    ]
    list_filter = ['status', 'data_vencimento', 'forma_pagamento']
    search_fields = ['numero', 'descricao']
    ordering = ['data_vencimento']
    readonly_fields = ['numero', 'valor_pendente', 'criado_em']
    date_hierarchy = 'data_vencimento'


@admin.register(LancamentoFinanceiro)
class LancamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = [
        'data_competencia', 'tipo', 'descricao', 'plano_contas',
        'valor', 'status', 'conta_bancaria',
    ]
    list_filter = ['tipo', 'status', 'data_competencia', 'recorrente']
    search_fields = ['descricao']
    ordering = ['-data_competencia']
    date_hierarchy = 'data_competencia'


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'banco', 'tipo', 'saldo_atual', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'banco']


@admin.register(PlanoContas)
class PlanoContasAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'tipo', 'pai', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['codigo', 'nome']
    ordering = ['codigo']
