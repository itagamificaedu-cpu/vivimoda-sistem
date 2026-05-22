"""
Models financeiros: ContaBancaria, PlanoContas, ContaReceber, ContaPagar, Lançamentos.
"""
import uuid
from django.db import models
from django.utils import timezone


class ContaBancaria(models.Model):
    TIPOS = [('CORRENTE','Corrente'),('POUPANCA','Poupança'),('CAIXA','Caixa Físico'),('PIX','Conta PIX')]

    nome = models.CharField('Nome', max_length=100)
    banco = models.CharField('Banco', max_length=100, blank=True)
    agencia = models.CharField('Agência', max_length=20, blank=True)
    conta = models.CharField('Conta', max_length=30, blank=True)
    tipo = models.CharField('Tipo', max_length=10, choices=TIPOS, default='CORRENTE')
    saldo_inicial = models.DecimalField('Saldo inicial', max_digits=12, decimal_places=2, default=0)
    saldo_atual = models.DecimalField('Saldo atual', max_digits=12, decimal_places=2, default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Conta Bancária'
        verbose_name_plural = 'Contas Bancárias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class PlanoContas(models.Model):
    TIPOS = [('RECEITA','Receita'),('DESPESA','Despesa')]

    codigo = models.CharField('Código', max_length=20)
    nome = models.CharField('Nome', max_length=100)
    tipo = models.CharField('Tipo', max_length=10, choices=TIPOS)
    pai = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                            related_name='filhos', verbose_name='Conta pai')
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Plano de Contas'
        verbose_name_plural = 'Planos de Contas'
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} — {self.nome}'


class ContaReceber(models.Model):
    STATUS = [
        ('PENDENTE','Pendente'),('PAGO','Pago'),('PARCIAL','Parcialmente Pago'),
        ('VENCIDO','Vencido'),('CANCELADO','Cancelado'),
    ]

    numero = models.CharField('Número', max_length=20, unique=True)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.PROTECT, verbose_name='Cliente')
    venda = models.ForeignKey('vendas.Venda', null=True, blank=True, on_delete=models.PROTECT,
                              verbose_name='Venda')
    descricao = models.CharField('Descrição', max_length=200)
    valor_original = models.DecimalField('Valor original', max_digits=12, decimal_places=2)
    valor_juros = models.DecimalField('Juros', max_digits=10, decimal_places=2, default=0)
    valor_multa = models.DecimalField('Multa', max_digits=10, decimal_places=2, default=0)
    valor_desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=0)
    valor_pago = models.DecimalField('Valor pago', max_digits=12, decimal_places=2, default=0)
    valor_pendente = models.DecimalField('Valor pendente', max_digits=12, decimal_places=2)
    data_emissao = models.DateField('Emissão', auto_now_add=True)
    data_vencimento = models.DateField('Vencimento')
    data_pagamento = models.DateField('Pagamento', null=True, blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS, default='PENDENTE')
    forma_recebimento = models.CharField('Forma de recebimento', max_length=30, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    parcela_numero = models.IntegerField('Parcela nº', default=1)
    parcela_total = models.IntegerField('Total de parcelas', default=1)
    carne_grupo = models.UUIDField('Grupo do carnê', null=True, blank=True, default=uuid.uuid4)
    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
        ordering = ['data_vencimento']
        indexes = [
            models.Index(fields=['status', 'data_vencimento']),
            models.Index(fields=['cliente', 'status']),
        ]

    def __str__(self):
        return f'{self.numero} — {self.cliente} — R$ {self.valor_pendente}'

    @property
    def dias_atraso(self):
        hoje = timezone.localdate()
        if self.data_vencimento < hoje and self.status in ('PENDENTE', 'PARCIAL'):
            return (hoje - self.data_vencimento).days
        return 0

    def save(self, *args, **kwargs):
        self.valor_pendente = (self.valor_original + self.valor_juros + self.valor_multa
                               - self.valor_desconto - self.valor_pago)
        super().save(*args, **kwargs)


class ContaPagar(models.Model):
    STATUS = [
        ('PENDENTE','Pendente'),('PAGO','Pago'),('PARCIAL','Parcialmente Pago'),
        ('VENCIDO','Vencido'),('CANCELADO','Cancelado'),
    ]

    numero = models.CharField('Número', max_length=20, unique=True)
    fornecedor = models.ForeignKey('fornecedores.Fornecedor', null=True, blank=True,
                                   on_delete=models.PROTECT, verbose_name='Fornecedor')
    compra = models.ForeignKey('compras.OrdemCompra', null=True, blank=True,
                               on_delete=models.PROTECT, verbose_name='Compra')
    descricao = models.CharField('Descrição', max_length=200)
    valor_original = models.DecimalField('Valor original', max_digits=12, decimal_places=2)
    valor_juros = models.DecimalField('Juros', max_digits=10, decimal_places=2, default=0)
    valor_multa = models.DecimalField('Multa', max_digits=10, decimal_places=2, default=0)
    valor_desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=0)
    valor_pago = models.DecimalField('Valor pago', max_digits=12, decimal_places=2, default=0)
    valor_pendente = models.DecimalField('Valor pendente', max_digits=12, decimal_places=2)
    data_emissao = models.DateField('Emissão', auto_now_add=True)
    data_vencimento = models.DateField('Vencimento')
    data_pagamento = models.DateField('Pagamento', null=True, blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS, default='PENDENTE')
    forma_pagamento = models.CharField('Forma de pagamento', max_length=30, blank=True)
    comprovante = models.FileField('Comprovante', upload_to='comprovantes/', blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True)
    parcela_numero = models.IntegerField('Parcela nº', default=1)
    parcela_total = models.IntegerField('Total de parcelas', default=1)
    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
        ordering = ['data_vencimento']
        indexes = [models.Index(fields=['status', 'data_vencimento'])]

    def __str__(self):
        return f'{self.numero} — {self.descricao} — R$ {self.valor_pendente}'

    def save(self, *args, **kwargs):
        self.valor_pendente = (self.valor_original + self.valor_juros + self.valor_multa
                               - self.valor_desconto - self.valor_pago)
        super().save(*args, **kwargs)


class LancamentoFinanceiro(models.Model):
    TIPOS = [('RECEITA','Receita'),('DESPESA','Despesa')]
    STATUS = [('PREVISTO','Previsto'),('REALIZADO','Realizado'),('CANCELADO','Cancelado')]
    RECORRENCIAS = [('MENSAL','Mensal'),('SEMANAL','Semanal'),('ANUAL','Anual')]

    tipo = models.CharField('Tipo', max_length=10, choices=TIPOS)
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, verbose_name='Plano de contas')
    descricao = models.CharField('Descrição', max_length=200)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    data_competencia = models.DateField('Competência')
    data_pagamento = models.DateField('Pagamento', null=True, blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS, default='PREVISTO')
    conta_bancaria = models.ForeignKey(ContaBancaria, null=True, blank=True, on_delete=models.PROTECT)
    recorrente = models.BooleanField('Recorrente', default=False)
    recorrencia = models.CharField('Recorrência', max_length=10, choices=RECORRENCIAS, blank=True)
    anexo = models.FileField('Anexo', upload_to='lancamentos/', blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True)
    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lançamento Financeiro'
        verbose_name_plural = 'Lançamentos Financeiros'
        ordering = ['-data_competencia']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.descricao} — R$ {self.valor}'
