from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal


@login_required
def index(request):
    return render(request, 'relatorios/index.html', {'titulo': 'Relatórios'})


@login_required
def vendas_periodo(request):
    inicio_str = request.GET.get('inicio', str(date(date.today().year, date.today().month, 1)))
    fim_str = request.GET.get('fim', str(date.today()))
    try:
        inicio = date.fromisoformat(inicio_str)
        fim = date.fromisoformat(fim_str)
    except ValueError:
        inicio = date(date.today().year, date.today().month, 1)
        fim = date.today()

    from apps.vendas.models import Venda, ItemVenda
    vendas = Venda.objects.filter(
        data_venda__date__range=[inicio, fim],
        status__in=['PAGO', 'PARCIAL']
    ).select_related('cliente', 'vendedor')

    total = vendas.aggregate(t=Sum('valor_total'))['t'] or 0
    qtd = vendas.count()
    ticket_medio = total / qtd if qtd else 0

    # Vendas por dia (para gráfico)
    por_dia = vendas.values('data_venda__date').annotate(
        total=Sum('valor_total'), qtd=Count('id')
    ).order_by('data_venda__date')

    # Por forma de pagamento
    from apps.vendas.models import PagamentoVenda
    por_forma = PagamentoVenda.objects.filter(
        venda__data_venda__date__range=[inicio, fim],
        venda__status__in=['PAGO', 'PARCIAL']
    ).values('forma').annotate(total=Sum('valor')).order_by('-total')

    return render(request, 'relatorios/vendas_periodo.html', {
        'titulo': 'Relatório de Vendas por Período',
        'inicio': inicio, 'fim': fim,
        'vendas': vendas[:100],
        'total': total, 'qtd': qtd, 'ticket_medio': ticket_medio,
        'por_dia': list(por_dia),
        'por_forma': list(por_forma),
    })


@login_required
def produtos_mais_vendidos(request):
    # Filtros de data — template usa data_de / data_ate
    data_de_str  = request.GET.get('data_de',  str(date(date.today().year, date.today().month, 1)))
    data_ate_str = request.GET.get('data_ate', str(date.today()))
    categoria_id = request.GET.get('categoria', '')
    try:
        data_de  = date.fromisoformat(data_de_str)
        data_ate = date.fromisoformat(data_ate_str)
    except ValueError:
        data_de  = date(date.today().year, date.today().month, 1)
        data_ate = date.today()

    from apps.vendas.models import ItemVenda
    from apps.produtos.models import Categoria

    qs = ItemVenda.objects.filter(
        venda__data_venda__date__range=[data_de, data_ate],
        venda__status__in=['PAGO', 'PARCIAL']
    )
    if categoria_id:
        qs = qs.filter(produto__categoria_id=categoria_id)

    ranking = qs.values(
        'produto_id',               # necessário para o {% url 'produtos:detalhe' %}
        'produto__pk',
        'produto__nome',
        'produto__codigo',
        'produto__categoria__nome',
    ).annotate(
        total_vendido=Sum('quantidade'),   # nome que o template usa
        receita=Sum('valor_total'),        # nome que o template usa
    ).order_by('-receita')[:50]

    categorias = Categoria.objects.filter(ativo=True).order_by('nome')

    return render(request, 'relatorios/produtos_mais_vendidos.html', {
        'titulo': 'Produtos Mais Vendidos',
        'data_de': data_de, 'data_ate': data_ate,
        'categoria_id': categoria_id,
        'categorias': categorias,
        'ranking': list(ranking),
    })


@login_required
def inadimplencia(request):
    from apps.financeiro.models import ContaReceber
    contas = ContaReceber.objects.filter(
        status__in=['PENDENTE', 'PARCIAL', 'VENCIDO'],
        data_vencimento__lt=date.today()
    ).select_related('cliente').order_by('-valor_pendente')

    total = contas.aggregate(t=Sum('valor_pendente'))['t'] or 0

    return render(request, 'relatorios/inadimplencia.html', {
        'titulo': 'Relatório de Inadimplência',
        'contas': contas[:200],
        'total': total,
        'hoje': date.today(),
    })


@login_required
def dre(request):
    """DRE simplificado do mês."""
    mes = int(request.GET.get('mes', date.today().month))
    ano = int(request.GET.get('ano', date.today().year))

    from apps.vendas.models import Venda
    from apps.financeiro.models import LancamentoFinanceiro, ContaReceber

    receita_bruta = Venda.objects.filter(
        data_venda__year=ano, data_venda__month=mes,
        status__in=['PAGO', 'PARCIAL']
    ).aggregate(t=Sum('valor_total'))['t'] or 0

    devolucoes = Venda.objects.filter(
        data_venda__year=ano, data_venda__month=mes,
        status='DEVOLVIDO'
    ).aggregate(t=Sum('valor_total'))['t'] or 0

    descontos = Venda.objects.filter(
        data_venda__year=ano, data_venda__month=mes,
        status__in=['PAGO', 'PARCIAL']
    ).aggregate(t=Sum('valor_desconto'))['t'] or 0

    receita_liquida = receita_bruta - devolucoes - descontos

    despesas = LancamentoFinanceiro.objects.filter(
        tipo='DESPESA', status='REALIZADO',
        data_competencia__year=ano, data_competencia__month=mes
    ).values('plano_contas__nome').annotate(total=Sum('valor')).order_by('-total')

    total_despesas = sum(d['total'] for d in despesas)
    resultado = receita_liquida - total_despesas

    return render(request, 'relatorios/dre.html', {
        'titulo': f'DRE — {mes:02d}/{ano}',
        'mes': mes, 'ano': ano,
        'receita_bruta': receita_bruta,
        'devolucoes': devolucoes,
        'descontos': descontos,
        'receita_liquida': receita_liquida,
        'despesas': list(despesas),
        'total_despesas': total_despesas,
        'resultado': resultado,
        'meses': range(1, 13),
        'anos': range(date.today().year - 2, date.today().year + 1),
    })


@login_required
def comissoes(request):
    inicio_str = request.GET.get('inicio', str(date(date.today().year, date.today().month, 1)))
    fim_str = request.GET.get('fim', str(date.today()))
    try:
        inicio = date.fromisoformat(inicio_str)
        fim = date.fromisoformat(fim_str)
    except ValueError:
        inicio = date(date.today().year, date.today().month, 1)
        fim = date.today()

    from apps.vendas.models import ItemVenda
    por_vendedor = ItemVenda.objects.filter(
        venda__data_venda__date__range=[inicio, fim],
        venda__status__in=['PAGO', 'PARCIAL'],
        venda__vendedor__isnull=False,
    ).values(
        'venda__vendedor__nome_completo'
    ).annotate(
        total_vendas=Sum('valor_total'),
        total_comissao=Sum('comissao_valor')
    ).order_by('-total_comissao')

    return render(request, 'relatorios/comissoes.html', {
        'titulo': 'Relatório de Comissões',
        'inicio': inicio, 'fim': fim,
        'por_vendedor': list(por_vendedor),
    })
