"""
Models de vendas: Venda, ItemVenda, PagamentoVenda.
"""
from django.db import models


class Venda(models.Model):
    STATUS = [
        ('ORCAMENTO','Orçamento'), ('PENDENTE','Pendente'), ('PAGO','Pago'),
        ('PARCIAL','Parcialmente Pago'), ('CANCELADO','Cancelado'), ('DEVOLVIDO','Devolvido'),
    ]
    CANAIS = [
        ('LOJA','Loja Física'), ('WHATSAPP','WhatsApp'), ('INSTAGRAM','Instagram'),
        ('SITE','Site'), ('TELEFONE','Telefone'),
    ]

    numero = models.CharField('Número', max_length=20, unique=True)
    cliente = models.ForeignKey('clientes.Cliente', null=True, blank=True,
                                on_delete=models.PROTECT, verbose_name='Cliente')
    vendedor = models.ForeignKey('funcionarios.Funcionario', null=True, blank=True,
                                 on_delete=models.PROTECT, verbose_name='Vendedor')

    data_venda = models.DateTimeField('Data da venda', auto_now_add=True)
    data_entrega = models.DateField('Data de entrega', null=True, blank=True)

    valor_produtos = models.DecimalField('Valor dos produtos', max_digits=12, decimal_places=2, default=0)
    valor_desconto = models.DecimalField('Desconto (R$)', max_digits=10, decimal_places=2, default=0)
    percentual_desconto = models.DecimalField('Desconto (%)', max_digits=5, decimal_places=2, default=0)
    valor_frete = models.DecimalField('Frete', max_digits=10, decimal_places=2, default=0)
    valor_total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    valor_pago = models.DecimalField('Valor pago', max_digits=12, decimal_places=2, default=0)
    valor_troco = models.DecimalField('Troco', max_digits=10, decimal_places=2, default=0)
    valor_pendente = models.DecimalField('Valor pendente', max_digits=12, decimal_places=2, default=0)

    status = models.CharField('Status', max_length=10, choices=STATUS, default='PENDENTE')
    canal = models.CharField('Canal', max_length=10, choices=CANAIS, default='LOJA')
    observacoes = models.TextField('Observações', blank=True)
    observacoes_internas = models.TextField('Observações internas', blank=True)

    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT,
                                related_name='vendas_realizadas')
    caixa = models.ForeignKey('caixa.SessaoCaixa', null=True, blank=True, on_delete=models.PROTECT)
    cancelado_por = models.ForeignKey('autenticacao.Usuario', null=True, blank=True,
                                      on_delete=models.PROTECT, related_name='vendas_canceladas')
    motivo_cancelamento = models.TextField('Motivo do cancelamento', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status', 'data_venda']),
            models.Index(fields=['cliente', 'status']),
            models.Index(fields=['numero']),
        ]

    def __str__(self):
        return f'Venda {self.numero} — {self.cliente or "Sem cadastro"} — R$ {self.valor_total}'

    def recalcular_totais(self):
        self.valor_produtos = sum(i.valor_total for i in self.itens.all())
        self.valor_total = self.valor_produtos - self.valor_desconto + self.valor_frete
        self.valor_pendente = max(0, self.valor_total - self.valor_pago)
        self.save(update_fields=['valor_produtos', 'valor_total', 'valor_pendente'])


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT)
    grade = models.ForeignKey('produtos.GradeProduto', null=True, blank=True, on_delete=models.PROTECT)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2)
    preco_unitario = models.DecimalField('Preço unitário', max_digits=10, decimal_places=2)
    desconto = models.DecimalField('Desconto (%)', max_digits=5, decimal_places=2, default=0)
    valor_total = models.DecimalField('Total', max_digits=12, decimal_places=2)
    comissao_percentual = models.DecimalField('Comissão (%)', max_digits=5, decimal_places=2, default=0)
    comissao_valor = models.DecimalField('Comissão (R$)', max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'

    def __str__(self):
        return f'{self.produto} x {self.quantidade}'

    def save(self, *args, **kwargs):
        desc = self.preco_unitario * self.quantidade * self.desconto / 100
        self.valor_total = self.preco_unitario * self.quantidade - desc
        self.comissao_valor = self.valor_total * self.comissao_percentual / 100
        super().save(*args, **kwargs)


class PagamentoVenda(models.Model):
    FORMAS = [
        ('DINHEIRO','Dinheiro'), ('PIX','PIX'), ('CARTAO_CREDITO','Cartão de Crédito'),
        ('CARTAO_DEBITO','Cartão de Débito'), ('CHEQUE','Cheque'),
        ('TRANSFERENCIA','Transferência'), ('CREDIARIO','Crediário'),
        ('CARNE','Carnê'), ('VALE','Vale/Crédito'),
    ]

    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='pagamentos')
    forma = models.CharField('Forma', max_length=20, choices=FORMAS)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    parcelas = models.IntegerField('Parcelas', default=1)
    data_pagamento = models.DateTimeField('Data', auto_now_add=True)
    nsu = models.CharField('NSU (cartão)', max_length=30, blank=True)
    bandeira = models.CharField('Bandeira', max_length=30, blank=True)
    vencimento_cheque = models.DateField('Vencimento do cheque', null=True, blank=True)
    comprovante = models.FileField('Comprovante', upload_to='comprovantes/', blank=True, null=True)
    observacoes = models.CharField('Observações', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Pagamento de Venda'
        verbose_name_plural = 'Pagamentos de Venda'

    def __str__(self):
        return f'{self.get_forma_display()} — R$ {self.valor}'
