from django.urls import path
from . import views

app_name = 'autenticacao'

urlpatterns = [
    path('login/', views.view_login, name='login'),
    path('logout/', views.view_logout, name='logout'),
    path('perfil/', views.view_perfil, name='perfil'),
    path('perfil/salvar/', views.salvar_perfil, name='salvar_perfil'),
    path('perfil/senha/', views.alterar_senha, name='alterar_senha'),
    path('usuarios/', views.view_usuarios, name='usuarios'),
    path('usuarios/novo/', views.view_criar_usuario, name='novo_usuario'),
    path('usuarios/<int:pk>/editar/', views.view_editar_usuario, name='editar_usuario'),
    path('logs/', views.view_logs, name='logs'),
]
