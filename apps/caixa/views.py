from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal

from .models import Caixa, SessaoCaixa, MovimentacaoCaixa


@login_required
def index(request):
    """Página principal do caixa — mostra sessão aberta ou opção de abrir."""
    caixas = Caixa.objects.filter(ativo=True)
    sessao_aberta = SessaoCaixa.objects.filter(
        operador=request.user, status='ABERTO'
    ).select_related('caixa').first()

    sessoes_recentes = SessaoCaixa.objects.select_related(
        'caixa', 'operador'
    ).order_by('-data_abertura')[:10]

    return render(request, 'caixa/index.html', {
        'titulo': 'Caixa',
        'caixas': caixas,
        'sessao_aberta': sessao_aberta,
        'sessoes_recentes': sessoes_recentes,
    })


@login_required
def abrir(request):
    """Abre uma nova sessão de caixa."""
    # Verifica se já há sessão aberta para este usuário
    if SessaoCaixa.objects.filter(operador=request.user, status='ABERTO').exists():
        messages.warning(request, 'Você já tem um caixa aberto!')
        return redirect('caixa:index')

    caixas = Caixa.objects.filter(ativo=True)

    if request.method == 'POST':
        caixa_id = request.POST.get('caixa_id', '').strip()
        if not caixa_id or not caixa_id.isdigit():
            messages.error(request, 'Selecione um caixa válido.')
            return render(request, 'caixa/abrir.html', {
                'titulo': 'Abrir Caixa', 'caixas': caixas,
            })

        try:
            valor_abertura = Decimal(request.POST.get('valor_abertura', '0') or '0')
        except Exception:
            valor_abertura = Decimal('0')

        caixa = get_object_or_404(Caixa, pk=caixa_id)

        # Verifica se o caixa já está aberto por outro operador
        if SessaoCaixa.objects.filter(caixa=caixa, status='ABERTO').exists():
            messages.error(request, f'{caixa} já está aberto por outro operador.')
            return redirect('caixa:index')

        sessao = SessaoCaixa.objects.create(
            caixa=caixa,
            operador=request.user,
            valor_abertura=valor_abertura,
        )
        MovimentacaoCaixa.objects.create(
            sessao=sessao, tipo='ABERTURA',
            valor=valor_abertura,
            descricao=f'Abertura do caixa com R$ {valor_abertura}',
            usuario=request.user,
        )
        messages.success(request, f'{caixa} aberto com R$ {valor_abertura}!')
        return redirect('caixa:sessao', pk=sessao.pk)

    # GET — pré-seleciona caixa se vier via ?caixa=pk
    caixa_selecionado_pk = request.GET.get('caixa', '').strip()
    caixa_obj = None
    if caixa_selecionado_pk and caixa_selecionado_pk.isdigit():
        caixa_obj = caixas.filter(pk=caixa_selecionado_pk).first()
    # Se há só um caixa, pré-seleciona automaticamente
    if not caixa_obj and caixas.count() == 1:
        caixa_obj = caixas.first()

    return render(request, 'caixa/abrir.html', {
        'titulo': 'Abrir Caixa',
        'caixas': caixas,
        'caixa': caixa_obj,
    })


@login_required
def sessao(request, pk):
    """Detalhes e movimentações de uma sessão de caixa."""
    sessao = get_object_or_404(SessaoCaixa.objects.select_related('caixa', 'operador'), pk=pk)
    movs = sessao.movimentacoes.select_related('usuario').order_by('-criado_em')

    return render(request, 'caixa/sessao.html', {
        'titulo': f'Sessão — {sessao.caixa}',
        'sessao': sessao, 'movimentacoes': movs,
    })


@login_required
def sangria(request, pk):
    """Registra sangria (retirada) do caixa — exige senha gerencial."""
    sessao = get_object_or_404(SessaoCaixa, pk=pk, status='ABERTO')

    if request.method == 'POST':
        valor = Decimal(request.POST.get('valor', '0'))
        descricao = request.POST.get('descricao', 'Sangria')
        senha = request.POST.get('senha_gerencial', '')

        # Valida senha gerencial (usuário master ou gerente)
        from django.contrib.auth import authenticate
        user = authenticate(username=request.user.username, password=senha)
        if not user and not _verificar_senha_gerencial(senha):
            messages.error(request, 'Senha gerencial inválida.')
            return redirect('caixa:sessao', pk=pk)

        sessao.valor_sangria += valor
        sessao.save(update_fields=['valor_sangria'])

        MovimentacaoCaixa.objects.create(
            sessao=sessao, tipo='SANGRIA',
            valor=valor, descricao=descricao,
            usuario=request.user,
        )
        messages.success(request, f'Sangria de R$ {valor} registrada.')
        return redirect('caixa:sessao', pk=pk)

    return render(request, 'caixa/sangria.html', {
        'titulo': 'Sangria de Caixa', 'sessao': sessao,
    })


@login_required
def suprimento(request, pk):
    sessao = get_object_or_404(SessaoCaixa, pk=pk, status='ABERTO')

    if request.method == 'POST':
        valor = Decimal(request.POST.get('valor', '0'))
        descricao = request.POST.get('descricao', 'Suprimento')

        sessao.valor_suprimento += valor
        sessao.save(update_fields=['valor_suprimento'])

        MovimentacaoCaixa.objects.create(
            sessao=sessao, tipo='SUPRIMENTO',
            valor=valor, descricao=descricao,
            usuario=request.user,
        )
        messages.success(request, f'Suprimento de R$ {valor} registrado.')
        return redirect('caixa:sessao', pk=pk)

    return render(request, 'caixa/suprimento.html', {
        'titulo': 'Suprimento de Caixa', 'sessao': sessao,
    })


@login_required
def fechar(request, pk):
    """Fechamento de caixa com conferência de valores."""
    sessao = get_object_or_404(SessaoCaixa, pk=pk, status='ABERTO')

    if request.method == 'POST':
        valor_contado = Decimal(request.POST.get('valor_contado_dinheiro', '0'))
        obs = request.POST.get('observacoes_fechamento', '')

        sessao.valor_contado_dinheiro = valor_contado
        sessao.diferenca_caixa = valor_contado - sessao.saldo_esperado
        sessao.observacoes_fechamento = obs
        sessao.status = 'FECHADO'
        sessao.data_fechamento = timezone.now()
        sessao.save()

        messages.success(request, 'Caixa fechado com sucesso!')
        return redirect('caixa:relatorio_fechamento', pk=pk)

    # Calcula totais por forma de pagamento das vendas da sessão
    from apps.vendas.models import PagamentoVenda
    pagamentos = PagamentoVenda.objects.filter(
        venda__caixa=sessao
    ).values('forma').annotate(total=models_sum('valor'))

    return render(request, 'caixa/fechar.html', {
        'titulo': 'Fechar Caixa', 'sessao': sessao,
        'pagamentos': list(pagamentos),
    })


def models_sum(campo):
    from django.db.models import Sum
    return Sum(campo)


@login_required
def relatorio_fechamento(request, pk):
    sessao = get_object_or_404(SessaoCaixa, pk=pk)
    movs = sessao.movimentacoes.all()
    return render(request, 'caixa/relatorio_fechamento.html', {
        'titulo': f'Relatório de Fechamento — {sessao.caixa}',
        'sessao': sessao, 'movimentacoes': movs,
    })


def _verificar_senha_gerencial(senha):
    """Verifica se existe um usuário master/gerente com esta senha."""
    from apps.autenticacao.models import Usuario
    from django.contrib.auth.hashers import check_password
    for u in Usuario.objects.filter(perfil__cargo__in=['master', 'gerente'], is_active=True):
        if u.check_password(senha):
            return True
    return False
