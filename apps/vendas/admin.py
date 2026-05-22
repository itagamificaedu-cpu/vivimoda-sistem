from django.contrib import admin
from .models import Venda, ItemVenda, PagamentoVenda

class ItemInline(admin.TabularInline):
    model = ItemVenda
    extra = 0

class PagamentoInline(admin.TabularInline):
    model = PagamentoVenda
    extra = 0

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'valor_total', 'status', 'data_venda', 'usuario']
    list_filter = ['status', 'canal', 'data_venda']
    search_fields = ['numero', 'cliente__nome']
    inlines = [ItemInline, PagamentoInline]
    ordering = ['-data_venda']
