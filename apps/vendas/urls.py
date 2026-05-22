from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('pdv/', views.pdv, name='pdv'),
    path('finalizar/', views.finalizar_venda, name='finalizar'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/cancelar/', views.cancelar, name='cancelar'),
    path('<int:pk>/cupom/', views.cupom, name='cupom'),
]
