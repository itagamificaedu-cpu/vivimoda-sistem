from django.urls import path
from . import views

app_name = 'caixa'

urlpatterns = [
    path('', views.index, name='index'),
    path('abrir/', views.abrir, name='abrir'),
    path('<int:pk>/', views.sessao, name='sessao'),
    path('<int:pk>/sangria/', views.sangria, name='sangria'),
    path('<int:pk>/suprimento/', views.suprimento, name='suprimento'),
    path('<int:pk>/fechar/', views.fechar, name='fechar'),
    path('<int:pk>/relatorio/', views.relatorio_fechamento, name='relatorio_fechamento'),
]
