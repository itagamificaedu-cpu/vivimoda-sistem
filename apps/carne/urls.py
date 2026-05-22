from django.urls import path
from . import views

app_name = 'carne'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('novo/', views.novo, name='novo'),
    path('<int:pk>/', views.detalhe, name='detalhe'),
    path('<int:pk>/imprimir/', views.imprimir_carne, name='imprimir'),
    path('<int:pk>/renegociar/', views.renegociar, name='renegociar'),
    path('parcela/<int:pk>/baixar/', views.baixar_parcela, name='baixar_parcela'),
]
