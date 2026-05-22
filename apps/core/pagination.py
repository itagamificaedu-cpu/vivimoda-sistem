"""
Paginação padrão para a API REST interna.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PaginacaoPadrao(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'por_pagina'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'paginas': self.page.paginator.num_pages,
            'pagina_atual': self.page.number,
            'proximo': self.get_next_link(),
            'anterior': self.get_previous_link(),
            'resultados': data,
        })
