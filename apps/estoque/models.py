"""
Models de controle de estoque: Movimentações e Inventário.
"""
from django.db import models


class MovimentacaoEstoque(models.Model):
    TIPOS = [
        ('ENTRADA_COMPRA', 'Entrada por Compra'),
        ('ENTRADA_DEVOLUCAO', 'Entrada por Devolução'),
        ('ENTRADA_AJUSTE', 'Entrada por Ajuste'),
        ('SAIDA_VENDA', 'Saída por Venda'),
        ('SAIDA_DEVOLUCAO', 'Saída Devolução a Fornecedor'),
        ('SAIDA_AJUSTE', 'Saída por Ajuste'),
        ('SAIDA_PERDA', 'Saída por Perda/Avaria'),
        ('TRANSFERENCIA', 'Transferência'),
    ]

    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT, verbose_name='Produto')
    grade = models.ForeignKey('produtos.GradeProduto', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Grade')
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2)
    custo_unitario = models.DecimalField('Custo unitário', max_digits=10, decimal_places=2, default=0)
    saldo_anterior = models.DecimalField('Saldo anterior', max_digits=10, decimal_places=2)
    saldo_atual = models.DecimalField('Saldo atual', max_digits=10, decimal_places=2)
    referencia_id = models.IntegerField('ID da referência', null=True, blank=True)
    referencia_tipo = models.CharField('Tipo da referência', max_length=50, blank=True)
    observacao = models.TextField('Observação', blank=True)
    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT, verbose_name='Usuário')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['produto', 'criado_em']),
            models.Index(fields=['tipo', 'criado_em']),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.produto} — {self.quantidade}'

    @property
    def eh_entrada(self):
        return self.tipo.startswith('ENTRADA')


class Inventario(models.Model):
    STATUS = [
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]

    descricao = models.CharField('Descrição', max_length=200)
    data_inicio = models.DateTimeField('Início', auto_now_add=True)
    data_fim = models.DateTimeField('Fim', null=True, blank=True)
    status = models.CharField('Status', max_length=15, choices=STATUS, default='EM_ANDAMENTO')
    usuario_responsavel = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT, verbose_name='Responsável')
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Inventário'
        verbose_name_plural = 'Inventários'
        ordering = ['-data_inicio']

    def __str__(self):
        return f'Inventário {self.data_inicio.strftime("%d/%m/%Y")} — {self.get_status_display()}'


class ItemInventario(models.Model):
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT)
    grade = models.ForeignKey('produtos.GradeProduto', null=True, blank=True, on_delete=models.PROTECT)
    estoque_sistema = models.DecimalField('Estoque sistema', max_digits=10, decimal_places=2)
    estoque_contado = models.DecimalField('Estoque contado', max_digits=10, decimal_places=2, null=True, blank=True)
    divergencia = models.DecimalField('Divergência', max_digits=10, decimal_places=2, null=True, blank=True)
    ajustado = models.BooleanField('Ajustado', default=False)

    class Meta:
        verbose_name = 'Item de Inventário'
        verbose_name_plural = 'Itens de Inventário'

    def __str__(self):
        return f'{self.produto} — contado: {self.estoque_contado}'

    def calcular_divergencia(self):
        if self.estoque_contado is not None:
            self.divergencia = self.estoque_contado - self.estoque_sistema
        return self.divergencia
