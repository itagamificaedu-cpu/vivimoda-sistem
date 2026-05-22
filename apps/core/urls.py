"""
URLs do core — dashboard principal e AJAX utilitários.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('ajax/buscar-cep/', views.ajax_buscar_cep, name='ajax_buscar_cep'),
    path('ajax/buscar-cnpj/', views.ajax_buscar_cnpj, name='ajax_buscar_cnpj'),
    path('ajax/dashboard-dados/', views.ajax_dashboard_dados, name='ajax_dashboard_dados'),
]
