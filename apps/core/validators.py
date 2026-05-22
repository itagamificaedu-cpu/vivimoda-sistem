"""
Validadores brasileiros: CPF, CNPJ, CEP, telefone.
"""
import re
from django.core.exceptions import ValidationError


def validar_cpf(cpf: str) -> bool:
    """Valida CPF com dígitos verificadores."""
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto in (10, 11):
        resto = 0
    if resto != int(cpf[9]):
        return False

    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto in (10, 11):
        resto = 0
    return resto == int(cpf[10])


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ com dígitos verificadores."""
    cnpj = re.sub(r'[^0-9]', '', str(cnpj))
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(c) * p for c, p in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    d1 = calcular_digito(cnpj[:12], pesos1)
    d2 = calcular_digito(cnpj[:13], pesos2)
    return cnpj[-2:] == f'{d1}{d2}'


def formatar_cpf(cpf: str) -> str:
    """Formata CPF: 000.000.000-00"""
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}' if len(cpf) == 11 else cpf


def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ: 00.000.000/0001-00"""
    cnpj = re.sub(r'[^0-9]', '', str(cnpj))
    return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}' if len(cnpj) == 14 else cnpj


def formatar_cep(cep: str) -> str:
    """Formata CEP: 00000-000"""
    cep = re.sub(r'[^0-9]', '', str(cep))
    return f'{cep[:5]}-{cep[5:8]}' if len(cep) == 8 else cep


def formatar_telefone(tel: str) -> str:
    """Formata telefone: (00) 00000-0000 ou (00) 0000-0000"""
    tel = re.sub(r'[^0-9]', '', str(tel))
    if len(tel) == 11:
        return f'({tel[:2]}) {tel[2:7]}-{tel[7:]}'
    elif len(tel) == 10:
        return f'({tel[:2]}) {tel[2:6]}-{tel[6:]}'
    return tel


# Validators para uso em model fields do Django
def cpf_validator(value):
    if value and not validar_cpf(value):
        raise ValidationError('CPF inválido.')


def cnpj_validator(value):
    if value and not validar_cnpj(value):
        raise ValidationError('CNPJ inválido.')
