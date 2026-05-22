"""
API AJAX endpoints de Financeiro.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('resumo/', api_views.resumo_financeiro, name='api_resumo_financeiro'),
]
