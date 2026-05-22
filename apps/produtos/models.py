"""
Models de produtos: Categoria, Marca, Cor, Tamanho, Produto, Grade, Fotos.
"""
from decimal import Decimal
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class SubCategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nome = models.CharField('Nome', max_length=100)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Subcategoria'
        verbose_name_plural = 'Subcategorias'
        ordering = ['nome']

    def __str__(self):
        return f'{self.categoria} > {self.nome}'


class Marca(models.Model):
    nome = models.CharField('Nome', max_length=100)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Cor(models.Model):
    nome = models.CharField('Nome', max_length=50)
    codigo_hex = models.CharField('Cor (hex)', max_length=7, blank=True)

    class Meta:
        verbose_name = 'Cor'
        verbose_name_plural = 'Cores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Tamanho(models.Model):
    TIPOS = [('ADULTO', 'Adulto'), ('INFANTIL', 'Infantil'), ('NUMERICO', 'Numérico')]
    nome = models.CharField('Nome', max_length=20)
    ordem = models.IntegerField('Ordem', default=0)
    tipo = models.CharField('Tipo', max_length=10, choices=TIPOS, default='ADULTO')

    class Meta:
        verbose_name = 'Tamanho'
        verbose_name_plural = 'Tamanhos'
        ordering = ['tipo', 'ordem', 'nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    TIPOS = [
        ('SIMPLES', 'Simples'),
        ('GRADE', 'Com Grade (cor/tamanho)'),
        ('KIT', 'Kit/Composição'),
    ]
    ORIGENS = [('0', 'Nacional'), ('1', 'Estrangeira')]

    # Identificação
    codigo = models.CharField('Código', max_length=50, unique=True)
    codigo_barras = models.CharField('Código de barras', max_length=50, unique=True, blank=True)
    referencia = models.CharField('Referência', max_length=100, blank=True)
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)

    # Classificação
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name='Categoria')
    subcategoria = models.ForeignKey(SubCategoria, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Subcategoria')
    marca = models.ForeignKey(Marca, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Marca')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPOS, default='SIMPLES')

    # Preços
    preco_custo = models.DecimalField('Preço de custo', max_digits=10, decimal_places=2, default=0)
    margem_lucro = models.DecimalField('Margem de lucro (%)', max_digits=5, decimal_places=2, default=0)
    preco_venda = models.DecimalField('Preço de venda', max_digits=10, decimal_places=2)
    preco_promocional = models.DecimalField('Preço promocional', max_digits=10, decimal_places=2, null=True, blank=True)
    promocao_inicio = models.DateField('Início da promoção', null=True, blank=True)
    promocao_fim = models.DateField('Fim da promoção', null=True, blank=True)

    # Estoque (para produto simples; grade tem estoque por variação)
    estoque_atual = models.DecimalField('Estoque atual', max_digits=10, decimal_places=2, default=0)
    estoque_minimo = models.DecimalField('Estoque mínimo', max_digits=10, decimal_places=2, default=0)
    estoque_maximo = models.DecimalField('Estoque máximo', max_digits=10, decimal_places=2, default=0)
    unidade = models.CharField('Unidade', max_length=10, default='UN')
    localizacao = models.CharField('Localização (prateleira)', max_length=50, blank=True)

    # Fiscal
    ncm = models.CharField('NCM', max_length=10, blank=True)
    cest = models.CharField('CEST', max_length=9, blank=True)
    cfop = models.CharField('CFOP', max_length=4, blank=True)
    origem = models.CharField('Origem', max_length=1, choices=ORIGENS, default='0')

    # Mídia
    foto_principal = models.ImageField('Foto principal', upload_to='produtos/', blank=True, null=True)

    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['ativo', 'categoria']),
        ]

    def __str__(self):
        return f'{self.codigo} — {self.nome}'

    @property
    def preco_vigente(self):
        """Retorna preço promocional se a promoção estiver ativa."""
        hoje = timezone.localdate()
        if (self.preco_promocional and self.promocao_inicio and self.promocao_fim
                and self.promocao_inicio <= hoje <= self.promocao_fim):
            return self.preco_promocional
        return self.preco_venda

    @property
    def em_promocao(self):
        hoje = timezone.localdate()
        return (self.preco_promocional and self.promocao_inicio and self.promocao_fim
                and self.promocao_inicio <= hoje <= self.promocao_fim)

    @property
    def estoque_baixo(self):
        return self.estoque_atual <= self.estoque_minimo and self.tipo == 'SIMPLES'

    def calcular_preco_pela_margem(self):
        """Recalcula preço de venda a partir do custo + margem."""
        if self.preco_custo and self.margem_lucro:
            self.preco_venda = self.preco_custo * (1 + self.margem_lucro / 100)
        return self.preco_venda


class GradeProduto(models.Model):
    """Variação de produto por cor e tamanho."""
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='grades')
    cor = models.ForeignKey(Cor, on_delete=models.PROTECT, verbose_name='Cor')
    tamanho = models.ForeignKey(Tamanho, on_delete=models.PROTECT, verbose_name='Tamanho')
    codigo_barras = models.CharField('Código de barras', max_length=50, unique=True, blank=True)
    preco_adicional = models.DecimalField('Preço adicional', max_digits=10, decimal_places=2, default=0)
    estoque_atual = models.DecimalField('Estoque atual', max_digits=10, decimal_places=2, default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Grade do Produto'
        verbose_name_plural = 'Grades dos Produtos'
        unique_together = [['produto', 'cor', 'tamanho']]
        ordering = ['tamanho__ordem', 'cor__nome']

    def __str__(self):
        return f'{self.produto.nome} — {self.cor} / {self.tamanho}'

    @property
    def preco_final(self):
        return self.produto.preco_vigente + self.preco_adicional


class FotoProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField('Imagem', upload_to='produtos/fotos/')
    legenda = models.CharField('Legenda', max_length=100, blank=True)
    ordem = models.IntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Foto do Produto'
        verbose_name_plural = 'Fotos dos Produtos'
        ordering = ['ordem']

    def __str__(self):
        return f'Foto {self.ordem} — {self.produto.nome}'


class HistoricoPreco(models.Model):
    """Rastreio de alterações de preço."""
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='historico_precos')
    preco_anterior = models.DecimalField('Preço anterior', max_digits=10, decimal_places=2)
    preco_novo = models.DecimalField('Preço novo', max_digits=10, decimal_places=2)
    motivo = models.CharField('Motivo', max_length=200, blank=True)
    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico de Preço'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.produto} — R$ {self.preco_novo}'
