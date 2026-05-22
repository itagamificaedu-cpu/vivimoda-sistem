"""
Model de Funcionário com dados pessoais, profissionais e bancários.
"""
from django.db import models
from apps.core.validators import cpf_validator


class Funcionario(models.Model):
    SEXOS = [('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')]
    ESTADOS_CIVIS = [
        ('SOLTEIRO', 'Solteiro(a)'), ('CASADO', 'Casado(a)'),
        ('DIVORCIADO', 'Divorciado(a)'), ('VIUVO', 'Viúvo(a)'), ('UNIAO', 'União Estável'),
    ]
    TIPOS_CONTRATO = [
        ('CLT', 'CLT'), ('PJ', 'PJ'), ('EST', 'Estágio'), ('AUT', 'Autônomo'),
    ]
    TIPOS_CONTA = [('CC', 'Corrente'), ('CP', 'Poupança')]

    # Dados pessoais
    nome_completo = models.CharField('Nome completo', max_length=200)
    cpf = models.CharField('CPF', max_length=14, unique=True, validators=[cpf_validator])
    rg = models.CharField('RG', max_length=20, blank=True)
    data_nascimento = models.DateField('Data de nascimento')
    sexo = models.CharField('Sexo', max_length=1, choices=SEXOS)
    estado_civil = models.CharField('Estado civil', max_length=15, choices=ESTADOS_CIVIS, blank=True)
    foto = models.ImageField('Foto', upload_to='funcionarios/', blank=True, null=True)

    # Contato
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    celular = models.CharField('Celular', max_length=20)
    email = models.EmailField('E-mail', blank=True)

    # Endereço
    cep = models.CharField('CEP', max_length=9, blank=True)
    logradouro = models.CharField('Logradouro', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=10, blank=True)
    complemento = models.CharField('Complemento', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)

    # Dados profissionais
    cargo = models.CharField('Cargo', max_length=100)
    setor = models.CharField('Setor', max_length=100, blank=True)
    salario = models.DecimalField('Salário', max_digits=10, decimal_places=2)
    comissao_percentual = models.DecimalField('Comissão (%)', max_digits=5, decimal_places=2, default=0)
    data_admissao = models.DateField('Data de admissão')
    data_demissao = models.DateField('Data de demissão', null=True, blank=True)
    tipo_contrato = models.CharField('Tipo de contrato', max_length=3, choices=TIPOS_CONTRATO, default='CLT')

    # Dados bancários
    banco = models.CharField('Banco', max_length=100, blank=True)
    agencia = models.CharField('Agência', max_length=20, blank=True)
    conta = models.CharField('Conta', max_length=30, blank=True)
    tipo_conta = models.CharField('Tipo de conta', max_length=2, choices=TIPOS_CONTA, blank=True)
    pix = models.CharField('Chave PIX', max_length=100, blank=True)

    # Documentos trabalhistas
    ctps_numero = models.CharField('CTPS Número', max_length=20, blank=True)
    ctps_serie = models.CharField('CTPS Série', max_length=10, blank=True)
    pis_pasep = models.CharField('PIS/PASEP', max_length=20, blank=True)

    # Sistema
    usuario = models.OneToOneField(
        'autenticacao.Usuario', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name='Usuário do sistema', related_name='funcionario'
    )
    ativo = models.BooleanField('Ativo', default=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome_completo']
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['ativo', 'cargo']),
        ]

    def __str__(self):
        return self.nome_completo

    @property
    def situacao(self):
        return 'Ativo' if self.ativo else 'Inativo'


class HistoricoSalario(models.Model):
    """Registro de alterações salariais."""
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='historico_salarios')
    salario_anterior = models.DecimalField('Salário anterior', max_digits=10, decimal_places=2)
    salario_novo = models.DecimalField('Salário novo', max_digits=10, decimal_places=2)
    motivo = models.CharField('Motivo', max_length=200, blank=True)
    data_alteracao = models.DateField('Data da alteração', auto_now_add=True)
    usuario = models.ForeignKey('autenticacao.Usuario', on_delete=models.PROTECT, verbose_name='Alterado por')

    class Meta:
        verbose_name = 'Histórico de Salário'
        verbose_name_plural = 'Históricos de Salário'
        ordering = ['-data_alteracao']

    def __str__(self):
        return f'{self.funcionario} — R$ {self.salario_novo} em {self.data_alteracao}'


class FeriasFuncionario(models.Model):
    """Controle de férias e afastamentos."""
    TIPOS = [
        ('FERIAS', 'Férias'), ('LICENCA', 'Licença Médica'),
        ('MATERNIDADE', 'Licença Maternidade'), ('AFASTAMENTO', 'Afastamento'),
    ]
    STATUS = [('AGENDADO', 'Agendado'), ('EM_CURSO', 'Em Curso'), ('CONCLUIDO', 'Concluído')]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='ferias')
    tipo = models.CharField('Tipo', max_length=15, choices=TIPOS, default='FERIAS')
    data_inicio = models.DateField('Início')
    data_fim = models.DateField('Fim')
    dias = models.IntegerField('Dias', default=0)
    status = models.CharField('Status', max_length=10, choices=STATUS, default='AGENDADO')
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Férias/Afastamento'
        verbose_name_plural = 'Férias/Afastamentos'
        ordering = ['-data_inicio']

    def __str__(self):
        return f'{self.funcionario} — {self.get_tipo_display()} ({self.data_inicio})'

    def save(self, *args, **kwargs):
        if self.data_inicio and self.data_fim:
            self.dias = (self.data_fim - self.data_inicio).days + 1
        super().save(*args, **kwargs)
