"""
API AJAX endpoints de Caixa — consulta de sessão ativa.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('sessao-ativa/', api_views.sessao_ativa, name='api_sessao_ativa'),
    path('saldo/<int:sessao_pk>/', api_views.saldo_sessao, name='api_saldo_sessao'),
]
