"""
Admin de Estoque — Movimentações e Inventários.
"""
from django.contrib import admin
from .models import MovimentacaoEstoque, Inventario, ItemInventario


class ItemInventarioInline(admin.TabularInline):
    model = ItemInventario
    extra = 0
    fields = ['produto', 'grade', 'estoque_sistema', 'estoque_contado', 'divergencia', 'ajustado']
    readonly_fields = ['estoque_sistema', 'divergencia', 'ajustado']


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = [
        'criado_em', 'produto', 'grade', 'tipo', 'quantidade',
        'saldo_anterior', 'saldo_atual', 'usuario',
    ]
    list_filter = ['tipo', 'criado_em']
    search_fields = ['produto__nome', 'produto__codigo', 'observacao']
    ordering = ['-criado_em']
    readonly_fields = [
        'produto', 'grade', 'tipo', 'quantidade', 'custo_unitario',
        'saldo_anterior', 'saldo_atual', 'referencia_id', 'referencia_tipo',
        'usuario', 'criado_em',
    ]
    date_hierarchy = 'criado_em'

    def has_add_permission(self, request):
        # Movimentações só devem ser criadas pelo sistema, nunca manualmente
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'data_inicio', 'data_fim', 'status', 'usuario_responsavel']
    list_filter = ['status', 'data_inicio']
    search_fields = ['descricao', 'usuario_responsavel__username']
    ordering = ['-data_inicio']
    inlines = [ItemInventarioInline]
    readonly_fields = ['data_inicio', 'data_fim']
