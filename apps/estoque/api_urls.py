"""
API AJAX endpoints de Estoque — consulta de saldo por produto/grade.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('saldo/<int:produto_pk>/', api_views.saldo_produto, name='api_saldo_produto'),
    path('saldo/grade/<int:grade_pk>/', api_views.saldo_grade, name='api_saldo_grade'),
]
