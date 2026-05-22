"""
Utilitários gerais do ConfecSystem.
"""
import re
import uuid
import requests
from decimal import Decimal
from django.utils import timezone


def gerar_numero_sequencial(model_class, campo='numero', prefixo='', tamanho=6):
    """
    Gera número sequencial para pedidos, vendas, etc.
    Ex: VD000001, CP000001
    """
    ultimo = model_class.objects.filter(**{f'{campo}__startswith': prefixo}).order_by(f'-{campo}').first()
    if ultimo:
        numero_atual = int(getattr(ultimo, campo).replace(prefixo, ''))
        proximo = numero_atual + 1
    else:
        proximo = 1
    return f'{prefixo}{str(proximo).zfill(tamanho)}'


def buscar_cep(cep: str) -> dict:
    """Consulta ViaCEP e retorna dados do endereço."""
    cep_limpo = re.sub(r'[^0-9]', '', cep)
    if len(cep_limpo) != 8:
        return {}
    try:
        resp = requests.get(f'https://viacep.com.br/ws/{cep_limpo}/json/', timeout=5)
        if resp.status_code == 200:
            dados = resp.json()
            if not dados.get('erro'):
                return {
                    'logradouro': dados.get('logradouro', ''),
                    'bairro': dados.get('bairro', ''),
                    'cidade': dados.get('localidade', ''),
                    'estado': dados.get('uf', ''),
                }
    except Exception:
        pass
    return {}


def buscar_cnpj(cnpj: str) -> dict:
    """Consulta API pública de CNPJ e retorna dados da empresa."""
    cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj_limpo) != 14:
        return {}
    try:
        resp = requests.get(f'https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}', timeout=5)
        if resp.status_code == 200:
            dados = resp.json()
            return {
                'razao_social': dados.get('razao_social', ''),
                'nome_fantasia': dados.get('nome_fantasia', ''),
                'logradouro': dados.get('logradouro', ''),
                'numero': dados.get('numero', ''),
                'complemento': dados.get('complemento', ''),
                'bairro': dados.get('bairro', ''),
                'cidade': dados.get('municipio', ''),
                'estado': dados.get('uf', ''),
                'cep': dados.get('cep', '').replace('.', '').replace('-', ''),
                'telefone': dados.get('ddd_telefone_1', ''),
                'email': dados.get('email', ''),
            }
    except Exception:
        pass
    return {}


def calcular_juros_simples(valor: Decimal, taxa_mensal: Decimal, dias_atraso: int) -> Decimal:
    """Calcula juros simples por dias de atraso."""
    if dias_atraso <= 0 or taxa_mensal <= 0:
        return Decimal('0')
    taxa_diaria = taxa_mensal / 30
    return (valor * taxa_diaria * dias_atraso / 100).quantize(Decimal('0.01'))


def calcular_multa(valor: Decimal, percentual_multa: Decimal) -> Decimal:
    """Calcula multa por atraso."""
    if percentual_multa <= 0:
        return Decimal('0')
    return (valor * percentual_multa / 100).quantize(Decimal('0.01'))


def valor_extenso(valor: Decimal) -> str:
    """Converte valor decimal em extenso (R$ 1.500,00 → um mil e quinhentos reais)."""
    # Implementação simplificada para valores comuns
    try:
        from num2words import num2words
        inteiro = int(valor)
        centavos = int((valor - inteiro) * 100)
        texto = num2words(inteiro, lang='pt_BR')
        if centavos:
            texto += f' reais e {num2words(centavos, lang="pt_BR")} centavos'
        else:
            texto += ' reais'
        return texto.capitalize()
    except ImportError:
        return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def dias_atraso(data_vencimento) -> int:
    """Retorna quantos dias em atraso (0 se não vencido)."""
    hoje = timezone.localdate()
    if data_vencimento < hoje:
        return (hoje - data_vencimento).days
    return 0
