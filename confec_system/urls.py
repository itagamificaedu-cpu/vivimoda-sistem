"""
URLs principais do ConfecSystem.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação
    path('auth/', include('apps.autenticacao.urls', namespace='autenticacao')),

    # Dashboard
    path('', include('apps.core.urls', namespace='core')),

    # Módulos
    path('funcionarios/', include('apps.funcionarios.urls', namespace='funcionarios')),
    path('clientes/', include('apps.clientes.urls', namespace='clientes')),
    path('fornecedores/', include('apps.fornecedores.urls', namespace='fornecedores')),
    path('produtos/', include('apps.produtos.urls', namespace='produtos')),
    path('estoque/', include('apps.estoque.urls', namespace='estoque')),
    path('compras/', include('apps.compras.urls', namespace='compras')),
    path('financeiro/', include('apps.financeiro.urls', namespace='financeiro')),
    path('caixa/', include('apps.caixa.urls', namespace='caixa')),
    path('vendas/', include('apps.vendas.urls', namespace='vendas')),
    path('carne/', include('apps.carne.urls', namespace='carne')),
    path('relatorios/', include('apps.relatorios.urls', namespace='relatorios')),
    path('configuracoes/', include('apps.configuracoes.urls', namespace='configuracoes')),

    # API REST interna (usada pelo AJAX do frontend)
    path('api/v1/', include('apps.core.api_urls')),
]

# Servir arquivos estáticos e de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]

# Personaliza o painel admin
admin.site.site_header = 'ConfecSystem — Administração'
admin.site.site_title = 'ConfecSystem'
admin.site.index_title = 'Painel de Administração'
