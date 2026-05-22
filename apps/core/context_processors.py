"""
Context processors — injeta dados globais em todos os templates.
"""
from django.conf import settings


def dados_globais(request):
    """Injeta nome do site e dados do usuário logado em todo template."""
    dados = {
        'SITE_NAME': settings.SITE_NAME,
        'usuario_logado': None,
        'perfil_usuario': None,
        'config_loja': None,
    }

    if request.user.is_authenticated:
        dados['usuario_logado'] = request.user
        if hasattr(request.user, 'perfil'):
            dados['perfil_usuario'] = request.user.perfil

        # Carrega configurações da loja (com cache para evitar query em toda requisição)
        try:
            from apps.configuracoes.models import ConfiguracaoLoja
            dados['config_loja'] = ConfiguracaoLoja.objects.first()
        except Exception:
            pass

    return dados
