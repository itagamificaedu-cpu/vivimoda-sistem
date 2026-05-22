"""
Model de Cliente — Pessoa Física e Jurídica.
"""
from django.db import models
from django.utils import timezone
from apps.core.validators import cpf_validator, cnpj_validator


class Cliente(models.Model):
    TIPOS = [('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')]
    SEXOS = [('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')]
    CATEGORIAS = [
        ('REGULAR', 'Regular'), ('VIP', 'VIP'),
        ('ATACADO', 'Atacado'), ('INADIMPLENTE', 'Inadimplente'),
    ]

    tipo = models.CharField('Tipo', max_length=2, choices=TIPOS, default='PF')

    # Pessoa Física
    nome = models.CharField('Nome', max_length=200)
    cpf = models.CharField('CPF', max_length=14, unique=True, null=True, blank=True, validators=[cpf_validator])
    rg = models.CharField('RG', max_length=20, blank=True)
    data_nascimento = models.DateField('Data de nascimento', null=True, blank=True)
    sexo = models.CharField('Sexo', max_length=1, choices=SEXOS, blank=True)

    # Pessoa Jurídica
    razao_social = models.CharField('Razão social', max_length=200, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True, null=True, blank=True, validators=[cnpj_validator])
    inscricao_estadual = models.CharField('Inscrição estadual', max_length=30, blank=True)
    nome_fantasia = models.CharField('Nome fantasia', max_length=200, blank=True)

    # Contato
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    celular = models.CharField('Celular', max_length=20)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)

    # Endereço
    cep = models.CharField('CEP', max_length=9, blank=True)
    logradouro = models.CharField('Logradouro', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=10, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2, blank=True)

    # Financeiro
    limite_credito = models.DecimalField('Limite de crédito', max_digits=10, decimal_places=2, default=0)
    saldo_devedor = models.DecimalField('Saldo devedor', max_digits=10, decimal_places=2, default=0)
    dia_vencimento = models.IntegerField('Dia de vencimento padrão', null=True, blank=True)

    # Classificação e fidelidade
    categoria = models.CharField('Categoria', max_length=15, choices=CATEGORIAS, default='REGULAR')
    pontos_fidelidade = models.IntegerField('Pontos de fidelidade', default=0)

    # Sistema
    foto = models.ImageField('Foto', upload_to='clientes/', blank=True, null=True)
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['cnpj']),
            models.Index(fields=['celular']),
            models.Index(fields=['ativo', 'categoria']),
        ]

    def __str__(self):
        return self.nome

    @property
    def nome_documento(self):
        return self.cpf or self.cnpj or '—'

    @property
    def aniversario_hoje(self):
        if self.data_nascimento:
            hoje = timezone.localdate()
            return self.data_nascimento.day == hoje.day and self.data_nascimento.month == hoje.month
        return False

    @property
    def inadimplente(self):
        return self.saldo_devedor > 0 or self.categoria == 'INADIMPLENTE'
