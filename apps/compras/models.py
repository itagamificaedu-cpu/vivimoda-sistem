"""
Models de compras: Ordem de Compra e itens.
"""
from django.db import models


class OrdemCompra(models.Model):
    STATUS = [
        ('RASCUNHO', 'Rascunho'),
        ('ENVIADO', 'Enviado ao Fornecedor'),
        ('PARCIAL', 'Recebido Parcialmente'),
        ('RECEBIDO', 'Recebido'),
        ('CANCELADO', 'Cancelado'),
    ]

    numero = models.CharField('Número', max_length=20, unique=True)
    fornecedor = models.ForeignKey('fornecedores.Fornecedor', on_delete=models.PROTECT, verbose_name='Fornecedor')
    data_pedido = models.DateField('Data do pedido', auto_now_add=True)
    data_previsao = models.DateField('Previsão de entrega', null=True, blank=True)
    data_recebimento = models.DateField('Data de recebimento', null=True, blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS, default='RASCUNHO')

    valor_produtos = models.DecimalField('Valor dos produtos', max_digits=12, decimal_places=2, default=0)
    valor_frete = models.DecimalField('Valor do frete', max_digits=10, decimal_places=2, default=0)
    valor_desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=0)
    valor_total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)

    condicao_pagamento = models.CharField('Condição de pagamento', max_length=100, blank=True)
    observacoes = models.TextField('Observações', blank=True)

    nf_numero = models.CharField('Número da NF', max_length=20, blank=True)
    nf_arquivo = models.FileField('Arquivo da NF', upload_to='nfs/', blank=True, null=True)

    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT, verbose_name='Criado por')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ordem de Compra'
        verbose_name_plural = 'Ordens de Compra'
        ordering = ['-criado_em']
        indexes = [models.Index(fields=['status', 'data_pedido'])]

    def __str__(self):
        return f'OC {self.numero} — {self.fornecedor}'

    def recalcular_totais(self):
        total_itens = sum(item.valor_total for item in self.itens.all())
        self.valor_produtos = total_itens
        self.valor_total = total_itens + self.valor_frete - self.valor_desconto
        self.save(update_fields=['valor_produtos', 'valor_total'])


class ItemOrdemCompra(models.Model):
    ordem = models.ForeignKey(OrdemCompra, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT)
    grade = models.ForeignKey('produtos.GradeProduto', null=True, blank=True, on_delete=models.PROTECT)
    quantidade_pedida = models.DecimalField('Qtd pedida', max_digits=10, decimal_places=2)
    quantidade_recebida = models.DecimalField('Qtd recebida', max_digits=10, decimal_places=2, default=0)
    preco_unitario = models.DecimalField('Preço unitário', max_digits=10, decimal_places=2)
    desconto = models.DecimalField('Desconto (%)', max_digits=5, decimal_places=2, default=0)
    valor_total = models.DecimalField('Total', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Item da Ordem de Compra'
        verbose_name_plural = 'Itens da Ordem de Compra'

    def __str__(self):
        return f'{self.produto} x {self.quantidade_pedida}'

    def save(self, *args, **kwargs):
        desconto_val = self.preco_unitario * self.quantidade_pedida * self.desconto / 100
        self.valor_total = self.preco_unitario * self.quantidade_pedida - desconto_val
        super().save(*args, **kwargs)
