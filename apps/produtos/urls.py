from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.criar, name='criar'),
    path('buscar/', views.buscar_ajax, name='buscar_ajax'),
    path('calcular-preco/', views.calcular_preco, name='calcular_preco'),
    path('categorias/', views.lista_categorias, name='categorias'),
    path('categorias/salvar/', views.salvar_categoria, name='salvar_categoria'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/excluir/', views.excluir, name='excluir'),
]
