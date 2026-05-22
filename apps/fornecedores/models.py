"""
Model de Fornecedor com múltiplos contatos e avaliação.
"""
from django.db import models
from apps.core.validators import cnpj_validator, cpf_validator


class Fornecedor(models.Model):
    TIPOS = [('PJ', 'Pessoa Jurídica'), ('PF', 'Pessoa Física')]
    AVALIACOES = [
        (1, '★ Ruim'), (2, '★★ Regular'), (3, '★★★ Bom'),
        (4, '★★★★ Muito Bom'), (5, '★★★★★ Excelente'),
    ]

    tipo = models.CharField('Tipo', max_length=2, choices=TIPOS, default='PJ')

    # Identificação
    razao_social = models.CharField('Razão social / Nome', max_length=200)
    nome_fantasia = models.CharField('Nome fantasia', max_length=200, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True, null=True, blank=True, validators=[cnpj_validator])
    cpf = models.CharField('CPF', max_length=14, unique=True, null=True, blank=True, validators=[cpf_validator])
    inscricao_estadual = models.CharField('Inscrição estadual', max_length=30, blank=True)

    # Contato principal
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    celular = models.CharField('Celular', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    site = models.URLField('Site', blank=True)

    # Endereço
    cep = models.CharField('CEP', max_length=9, blank=True)
    logradouro = models.CharField('Logradouro', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=10, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)

    # Condições comerciais
    prazo_pagamento = models.IntegerField('Prazo de pagamento (dias)', default=30)
    condicao_pagamento = models.CharField('Condição de pagamento', max_length=100, blank=True)
    desconto_padrao = models.DecimalField('Desconto padrão (%)', max_digits=5, decimal_places=2, default=0)

    # Avaliação
    avaliacao = models.IntegerField('Avaliação', choices=AVALIACOES, null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)

    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['razao_social']
        indexes = [
            models.Index(fields=['cnpj']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self):
        return self.nome_fantasia or self.razao_social

    @property
    def nome_exibicao(self):
        return self.nome_fantasia or self.razao_social


class ContatoFornecedor(models.Model):
    """Contatos adicionais do fornecedor (representantes, financeiro, etc)."""
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='contatos')
    nome = models.CharField('Nome', max_length=100)
    cargo = models.CharField('Cargo', max_length=100, blank=True)
    celular = models.CharField('Celular', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    principal = models.BooleanField('Contato principal', default=False)

    class Meta:
        verbose_name = 'Contato do Fornecedor'
        verbose_name_plural = 'Contatos dos Fornecedores'

    def __str__(self):
        return f'{self.nome} ({self.fornecedor})'


class AnexoFornecedor(models.Model):
    """Arquivos anexos: contratos, catálogos, etc."""
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='anexos')
    descricao = models.CharField('Descrição', max_length=200)
    arquivo = models.FileField('Arquivo', upload_to='fornecedores/anexos/')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anexo do Fornecedor'
        verbose_name_plural = 'Anexos dos Fornecedores'

    def __str__(self):
        return f'{self.descricao} — {self.fornecedor}'
