from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.index, name='index'),
    path('vendas/', views.vendas_periodo, name='vendas_periodo'),
    path('produtos-vendidos/', views.produtos_mais_vendidos, name='produtos_mais_vendidos'),
    path('inadimplencia/', views.inadimplencia, name='inadimplencia'),
    path('dre/', views.dre, name='dre'),
    path('comissoes/', views.comissoes, name='comissoes'),
]
