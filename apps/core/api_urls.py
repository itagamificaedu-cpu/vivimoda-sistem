"""
URLs da API REST interna — usadas pelo frontend via AJAX.
"""
from django.urls import path, include

urlpatterns = [
    path('produtos/', include('apps.produtos.api_urls')),
    path('clientes/', include('apps.clientes.api_urls')),
    path('estoque/', include('apps.estoque.api_urls')),
    path('financeiro/', include('apps.financeiro.api_urls')),
    path('caixa/', include('apps.caixa.api_urls')),
]
