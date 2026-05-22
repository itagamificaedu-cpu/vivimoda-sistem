"""
API AJAX endpoints de Produtos — busca por código de barras, nome, etc.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('buscar/', api_views.buscar_produto, name='api_buscar_produto'),
    path('<int:pk>/', api_views.detalhe_produto, name='api_detalhe_produto'),
]
