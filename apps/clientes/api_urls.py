"""
API AJAX endpoints de Clientes — busca por nome/CPF/celular.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('buscar/', api_views.buscar_cliente, name='api_buscar_cliente'),
    path('<int:pk>/', api_views.detalhe_cliente, name='api_detalhe_cliente'),
]
