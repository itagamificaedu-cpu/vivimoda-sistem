from django.contrib import admin
from .models import Carne, ParcelaCarne

class ParcelaInline(admin.TabularInline):
    model = ParcelaCarne
    extra = 0

@admin.register(Carne)
class CarneAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'valor_total', 'quantidade_parcelas', 'status', 'criado_em']
    list_filter = ['status']
    search_fields = ['numero', 'cliente__nome']
    inlines = [ParcelaInline]

@admin.register(ParcelaCarne)
class ParcelaCarneAdmin(admin.ModelAdmin):
    list_display = ['carne', 'numero', 'valor_original', 'data_vencimento', 'status']
    list_filter = ['status', 'data_vencimento']
