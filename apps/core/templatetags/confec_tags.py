"""
Template tags e filtros customizados do ConfecSystem.

Uso nos templates:
    {% load confec_tags %}
"""
from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()


# ── Filtros matemáticos ──────────────────────────────────────────────────────

@register.filter(name='mul')
def mul(value, arg):
    """Multiplica value por arg. Ex: {{ preco|mul:quantidade }}"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (InvalidOperation, TypeError, ValueError):
        return ''


@register.filter(name='div')
def div(value, arg):
    """Divide value por arg. Ex: {{ total|div:100 }}"""
    try:
        d = Decimal(str(arg))
        if d == 0:
            return ''
        return Decimal(str(value)) / d
    except (InvalidOperation, TypeError, ValueError):
        return ''


@register.filter(name='sub')
def sub(value, arg):
    """Subtrai arg de value. Ex: {{ total|sub:desconto }}"""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (InvalidOperation, TypeError, ValueError):
        return ''


@register.filter(name='percentage')
def percentage(value, total):
    """Calcula percentual de value sobre total. Ex: {{ pago|percentage:total }}"""
    try:
        t = Decimal(str(total))
        if t == 0:
            return Decimal('0')
        return (Decimal(str(value)) / t * 100).quantize(Decimal('0.1'))
    except (InvalidOperation, TypeError, ValueError):
        return ''


# ── Filtros de formatação monetária ─────────────────────────────────────────

@register.filter(name='moeda')
def moeda(value):
    """Formata como moeda BRL. Ex: {{ preco|moeda }} => R$ 1.234,56"""
    try:
        v = Decimal(str(value))
        # Formata com separador de milhar e 2 casas decimais
        formatted = f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f'R$ {formatted}'
    except (InvalidOperation, TypeError, ValueError):
        return 'R$ 0,00'


@register.filter(name='abs_value')
def abs_value(value):
    """Retorna valor absoluto. Ex: {{ divergencia|abs_value }}"""
    try:
        return abs(Decimal(str(value)))
    except (InvalidOperation, TypeError, ValueError):
        return value


# ── Filtros de texto ─────────────────────────────────────────────────────────

@register.filter(name='cpf_format')
def cpf_format(value):
    """Formata CPF: 12345678901 -> 123.456.789-01"""
    if not value:
        return ''
    v = str(value).strip().replace('.', '').replace('-', '')
    if len(v) == 11:
        return f'{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}'
    return value


@register.filter(name='cnpj_format')
def cnpj_format(value):
    """Formata CNPJ: 12345678000195 -> 12.345.678/0001-95"""
    if not value:
        return ''
    v = str(value).strip().replace('.', '').replace('/', '').replace('-', '')
    if len(v) == 14:
        return f'{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}'
    return value
