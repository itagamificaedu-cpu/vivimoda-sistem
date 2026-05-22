"""
Admin de Caixa — Sessões e Movimentações.
"""
from django.contrib import admin
from .models import Caixa, SessaoCaixa, MovimentacaoCaixa


class MovimentacaoInline(admin.TabularInline):
    model = MovimentacaoCaixa
    extra = 0
    fields = ['tipo', 'valor', 'descricao', 'usuario', 'criado_em']
    readonly_fields = ['tipo', 'valor', 'descricao', 'usuario', 'criado_em']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'descricao', 'ativo']
    list_filter = ['ativo']
    search_fields = ['numero', 'descricao']


@admin.register(SessaoCaixa)
class SessaoCaixaAdmin(admin.ModelAdmin):
    list_display = [
        'caixa', 'operador', 'data_abertura', 'data_fechamento',
        'valor_abertura', 'total_vendas', 'total_dinheiro', 'status',
    ]
    list_filter = ['status', 'caixa', 'data_abertura']
    search_fields = ['operador__username', 'caixa__numero']
    ordering = ['-data_abertura']
    date_hierarchy = 'data_abertura'
    inlines = [MovimentacaoInline]
    readonly_fields = [
        'caixa', 'operador', 'data_abertura', 'data_fechamento',
        'valor_abertura', 'valor_suprimento', 'valor_sangria',
        'total_dinheiro', 'total_pix', 'total_credito', 'total_debito',
        'total_crediario', 'total_outros', 'total_vendas',
        'valor_contado_dinheiro', 'diferenca_caixa', 'status',
    ]
    fieldsets = (
        ('Sessão', {
            'fields': ('caixa', 'operador', 'status', 'data_abertura', 'data_fechamento')
        }),
        ('Movimentos Financeiros', {
            'fields': (
                'valor_abertura', 'valor_suprimento', 'valor_sangria',
            )
        }),
        ('Totais por Forma de Pagamento', {
            'fields': (
                'total_dinheiro', 'total_pix', 'total_credito',
                'total_debito', 'total_crediario', 'total_outros', 'total_vendas',
            )
        }),
        ('Fechamento', {
            'fields': ('valor_contado_dinheiro', 'diferenca_caixa', 'observacoes_fechamento')
        }),
    )

    def has_add_permission(self, request):
        return False


@admin.register(MovimentacaoCaixa)
class MovimentacaoCaixaAdmin(admin.ModelAdmin):
    list_display = ['criado_em', 'sessao', 'tipo', 'valor', 'descricao', 'usuario']
    list_filter = ['tipo', 'criado_em']
    search_fields = ['descricao', 'referencia']
    ordering = ['-criado_em']
    readonly_fields = ['sessao', 'tipo', 'valor', 'descricao', 'referencia', 'usuario', 'criado_em']
    date_hierarchy = 'criado_em'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
