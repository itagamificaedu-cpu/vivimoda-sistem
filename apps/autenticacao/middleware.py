"""
Middleware de auditoria — registra ações sensíveis automaticamente.
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class AuditoriaMiddleware(MiddlewareMixin):
    """Registra ações POST sensíveis no LogAcesso."""

    # Padrões de URL que disparam log automático
    URLS_MONITORADAS = [
        '/vendas/nova/',
        '/vendas/cancelar/',
        '/caixa/abrir/',
        '/caixa/fechar/',
        '/caixa/sangria/',
        '/financeiro/baixar/',
        '/carne/baixar/',
        '/produtos/',
        '/clientes/',
        '/funcionarios/',
    ]

    def process_response(self, request, response):
        if not request.user.is_authenticated:
            return response
        if request.method != 'POST':
            return response

        path = request.path
        monitorada = any(path.startswith(url) for url in self.URLS_MONITORADAS)

        if monitorada and response.status_code in (200, 302):
            try:
                from .models import LogAcesso
                acao = 'CRIAR'
                if 'editar' in path or 'alterar' in path:
                    acao = 'EDITAR'
                elif 'excluir' in path or 'deletar' in path:
                    acao = 'EXCLUIR'
                elif 'cancelar' in path:
                    acao = 'CANCELAR'
                elif 'baixar' in path:
                    acao = 'BAIXAR'

                LogAcesso.objects.create(
                    usuario=request.user,
                    acao=acao,
                    modelo=path.split('/')[1],
                    ip=self._get_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    descricao=f'POST {path}',
                )
            except Exception:
                pass  # Nunca deixar auditoria quebrar a requisição

        return response

    def _get_ip(self, request) -> str:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
