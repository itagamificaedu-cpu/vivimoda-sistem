from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.index, name='index'),
    path('movimentacoes/', views.movimentacoes, name='movimentacoes'),
    path('ajuste/', views.ajuste_manual, name='ajuste'),
    # Inventários — nomes alinhados com templates
    path('inventarios/', views.inventario_lista, name='inventario_lista'),
    path('inventarios/novo/', views.inventario_novo, name='novo_inventario'),
    path('inventarios/<int:pk>/', views.inventario_detalhe, name='inventario_detalhe'),
    path('inventarios/<int:pk>/salvar/', views.inventario_salvar, name='inventario_salvar'),
    path('inventarios/<int:pk>/finalizar/', views.inventario_finalizar, name='inventario_finalizar'),
]
