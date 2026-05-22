from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    # Contas a Receber
    path('receber/', views.receber, name='receber'),
    path('receber/nova/', views.nova_conta_receber, name='nova_receber'),
    path('receber/<int:pk>/editar/', views.editar_conta_receber, name='editar_receber'),
    path('receber/<int:pk>/baixar/', views.baixar_recebimento, name='baixar_recebimento'),
    # Contas a Pagar
    path('pagar/', views.pagar, name='pagar'),
    path('pagar/nova/', views.nova_conta_pagar, name='nova_pagar'),
    path('pagar/<int:pk>/editar/', views.editar_conta_pagar, name='editar_pagar'),
    path('pagar/<int:pk>/baixar/', views.baixar_pagamento, name='baixar_pagamento'),
    # Lançamentos
    path('lancamentos/', views.lancamentos, name='lancamentos'),
    path('lancamentos/novo/', views.novo_lancamento, name='novo_lancamento'),
    # Fluxo de Caixa
    path('fluxo-caixa/', views.fluxo_caixa, name='fluxo_caixa'),
]
