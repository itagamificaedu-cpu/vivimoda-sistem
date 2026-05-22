from django.contrib import admin
from .models import Produto, GradeProduto, Categoria, SubCategoria, Marca, Cor, Tamanho, FotoProduto

class GradeInline(admin.TabularInline):
    model = GradeProduto
    extra = 0

class FotoInline(admin.TabularInline):
    model = FotoProduto
    extra = 0

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'categoria', 'preco_venda', 'estoque_atual', 'ativo']
    list_filter = ['categoria', 'ativo', 'tipo']
    search_fields = ['codigo', 'nome', 'codigo_barras', 'referencia']
    inlines = [GradeInline, FotoInline]
    ordering = ['nome']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']

admin.site.register(Marca)
admin.site.register(Cor)
admin.site.register(Tamanho)
admin.site.register(SubCategoria)
