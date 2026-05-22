"""
Models de Carnê / Crediário — parcelas, baixas e renegociação.
"""
from django.db import models
from django.utils import timezone


class Carne(models.Model):
    STATUS = [
        ('ATIVO','Ativo'), ('QUITADO','Quitado'),
        ('CANCELADO','Cancelado'), ('RENEGOCIADO','Renegociado'),
    ]

    numero = models.CharField('Número', max_length=20, unique=True)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.PROTECT, verbose_name='Cliente')
    venda = models.ForeignKey('vendas.Venda', null=True, blank=True,
                              on_delete=models.PROTECT, verbose_name='Venda')
    valor_total = models.DecimalField('Valor total', max_digits=12, decimal_places=2)
    entrada = models.DecimalField('Entrada', max_digits=10, decimal_places=2, default=0)
    quantidade_parcelas = models.IntegerField('Quantidade de parcelas')
    valor_parcela = models.DecimalField('Valor da parcela', max_digits=10, decimal_places=2)
    dia_vencimento = models.IntegerField('Dia de vencimento')
    taxa_juros = models.DecimalField('Taxa de juros (% a.m.)', max_digits=5, decimal_places=2, default=0)
    data_emissao = models.DateField('Emissão', auto_now_add=True)
    status = models.CharField('Status', max_length=12, choices=STATUS, default='ATIVO')
    carne_original = models.ForeignKey('self', null=True, blank=True,
                                       on_delete=models.SET_NULL,
                                       related_name='renegociacoes',
                                       verbose_name='Carnê original (renegociação)')
    observacoes = models.TextField('Observações', blank=True)
    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Carnê'
        verbose_name_plural = 'Carnês'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['cliente', 'status']),
            models.Index(fields=['status', 'criado_em']),
        ]

    def __str__(self):
        return f'Carnê {self.numero} — {self.cliente}'

    @property
    def valor_pago(self):
        return sum(p.valor_pago for p in self.parcelas.filter(status='PAGO'))

    @property
    def valor_pendente(self):
        return sum(
            p.valor_original + p.valor_juros + p.valor_multa - p.valor_desconto - p.valor_pago
            for p in self.parcelas.exclude(status__in=['PAGO','CANCELADO'])
        )

    @property
    def parcelas_vencidas(self):
        hoje = timezone.localdate()
        return self.parcelas.filter(data_vencimento__lt=hoje, status='PENDENTE').count()

    def gerar_parcelas(self):
        """Gera as parcelas após salvar o carnê."""
        from datetime import date
        import calendar

        self.parcelas.all().delete()
        hoje = date.today()

        for i in range(1, self.quantidade_parcelas + 1):
            # Calcula mês e ano do vencimento
            mes_offset = hoje.month + i - 1
            ano = hoje.year + (mes_offset - 1) // 12
            mes = ((mes_offset - 1) % 12) + 1
            # Ajusta para último dia do mês se necessário
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            dia = min(self.dia_vencimento, ultimo_dia)

            ParcelaCarne.objects.create(
                carne=self,
                numero=i,
                valor_original=self.valor_parcela,
                data_vencimento=date(ano, mes, dia),
            )


class ParcelaCarne(models.Model):
    STATUS = [
        ('PENDENTE','Pendente'), ('PAGO','Pago'),
        ('VENCIDO','Vencido'), ('CANCELADO','Cancelado'),
    ]

    carne = models.ForeignKey(Carne, on_delete=models.CASCADE, related_name='parcelas')
    numero = models.IntegerField('Número da parcela')
    valor_original = models.DecimalField('Valor original', max_digits=10, decimal_places=2)
    valor_juros = models.DecimalField('Juros', max_digits=10, decimal_places=2, default=0)
    valor_multa = models.DecimalField('Multa', max_digits=10, decimal_places=2, default=0)
    valor_desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=0)
    valor_pago = models.DecimalField('Valor pago', max_digits=10, decimal_places=2, default=0)
    data_vencimento = models.DateField('Vencimento')
    data_pagamento = models.DateField('Pagamento', null=True, blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS, default='PENDENTE')
    forma_pagamento = models.CharField('Forma de pagamento', max_length=30, blank=True)
    sessao_caixa = models.ForeignKey('caixa.SessaoCaixa', null=True, blank=True,
                                     on_delete=models.PROTECT, verbose_name='Sessão de caixa')
    usuario_baixa = models.ForeignKey('autenticacao.Usuario', null=True, blank=True,
                                      on_delete=models.PROTECT, verbose_name='Baixado por')

    class Meta:
        verbose_name = 'Parcela do Carnê'
        verbose_name_plural = 'Parcelas do Carnê'
        ordering = ['numero']
        indexes = [models.Index(fields=['status', 'data_vencimento'])]

    def __str__(self):
        return f'Parcela {self.numero}/{self.carne.quantidade_parcelas} — {self.carne.cliente}'

    @property
    def valor_a_pagar(self):
        return self.valor_original + self.valor_juros + self.valor_multa - self.valor_desconto

    @property
    def dias_atraso(self):
        hoje = timezone.localdate()
        if self.data_vencimento < hoje and self.status in ('PENDENTE', 'VENCIDO'):
            return (hoje - self.data_vencimento).days
        return 0
