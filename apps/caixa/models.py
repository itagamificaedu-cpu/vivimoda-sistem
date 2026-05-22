"""
Models de caixa: Caixa físico, Sessão e Movimentações.
"""
from django.db import models


class Caixa(models.Model):
    numero = models.CharField('Número', max_length=10)
    descricao = models.CharField('Descrição', max_length=100)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Caixa'
        verbose_name_plural = 'Caixas'
        ordering = ['numero']

    def __str__(self):
        return f'Caixa {self.numero} — {self.descricao}'

    @property
    def sessao_aberta(self):
        return self.sessoes.filter(status='ABERTO').first()


class SessaoCaixa(models.Model):
    STATUS = [('ABERTO','Aberto'),('FECHADO','Fechado')]

    caixa = models.ForeignKey(Caixa, on_delete=models.PROTECT, related_name='sessoes')
    operador = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT, verbose_name='Operador')
    data_abertura = models.DateTimeField('Abertura', auto_now_add=True)
    data_fechamento = models.DateTimeField('Fechamento', null=True, blank=True)
    valor_abertura = models.DecimalField('Valor de abertura', max_digits=10, decimal_places=2, default=0)
    valor_suprimento = models.DecimalField('Suprimentos', max_digits=10, decimal_places=2, default=0)
    valor_sangria = models.DecimalField('Sangrias', max_digits=10, decimal_places=2, default=0)

    # Totais por forma de pagamento
    total_dinheiro = models.DecimalField('Total Dinheiro', max_digits=12, decimal_places=2, default=0)
    total_pix = models.DecimalField('Total PIX', max_digits=12, decimal_places=2, default=0)
    total_credito = models.DecimalField('Total Crédito', max_digits=12, decimal_places=2, default=0)
    total_debito = models.DecimalField('Total Débito', max_digits=12, decimal_places=2, default=0)
    total_crediario = models.DecimalField('Total Crediário', max_digits=12, decimal_places=2, default=0)
    total_outros = models.DecimalField('Total Outros', max_digits=12, decimal_places=2, default=0)
    total_vendas = models.DecimalField('Total Vendas', max_digits=12, decimal_places=2, default=0)

    # Conferência no fechamento
    valor_contado_dinheiro = models.DecimalField('Dinheiro contado', max_digits=10, decimal_places=2, null=True, blank=True)
    diferenca_caixa = models.DecimalField('Diferença', max_digits=10, decimal_places=2, null=True, blank=True)
    observacoes_fechamento = models.TextField('Observações do fechamento', blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS, default='ABERTO')

    class Meta:
        verbose_name = 'Sessão de Caixa'
        verbose_name_plural = 'Sessões de Caixa'
        ordering = ['-data_abertura']

    def __str__(self):
        return f'{self.caixa} — {self.operador} — {self.data_abertura.strftime("%d/%m/%Y %H:%M")}'

    @property
    def saldo_esperado(self):
        return self.valor_abertura + self.valor_suprimento + self.total_dinheiro - self.valor_sangria


class MovimentacaoCaixa(models.Model):
    TIPOS = [
        ('ABERTURA','Abertura'), ('SUPRIMENTO','Suprimento'), ('SANGRIA','Sangria'),
        ('RECEBIMENTO','Recebimento'), ('PAGAMENTO','Pagamento'),
        ('VENDA','Venda'), ('DEVOLUCAO','Devolução'),
    ]

    sessao = models.ForeignKey(SessaoCaixa, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField('Tipo', max_length=15, choices=TIPOS)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    descricao = models.CharField('Descrição', max_length=200)
    referencia = models.CharField('Referência', max_length=100, blank=True)
    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação de Caixa'
        verbose_name_plural = 'Movimentações de Caixa'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.get_tipo_display()} — R$ {self.valor} — {self.criado_em.strftime("%H:%M")}'
