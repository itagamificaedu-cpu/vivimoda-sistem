"""
Configurações globais da loja — singleton (apenas um registro).
"""
from django.db import models
from django.core.exceptions import ValidationError


class ConfiguracaoLoja(models.Model):
    """Configurações principais da loja. Apenas um registro permitido."""

    # Dados da empresa
    nome_fantasia = models.CharField('Nome fantasia', max_length=200, default='Minha Loja')
    razao_social = models.CharField('Razão social', max_length=200, blank=True)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=18, blank=True)
    inscricao_estadual = models.CharField('Inscrição estadual', max_length=30, blank=True)
    logo = models.ImageField('Logo', upload_to='config/', blank=True, null=True)

    # Endereço
    endereco = models.CharField('Endereço', max_length=300, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    cep = models.CharField('CEP', max_length=9, blank=True)

    # Contato
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    site = models.URLField('Site', blank=True)
    instagram = models.CharField('Instagram', max_length=100, blank=True)

    # Dados bancários para recebimento
    pix_chave = models.CharField('Chave PIX', max_length=100, blank=True)
    pix_tipo = models.CharField('Tipo PIX', max_length=20, blank=True,
                                 choices=[('CPF','CPF'),('CNPJ','CNPJ'),('EMAIL','E-mail'),('CELULAR','Celular'),('ALEATORIA','Aleatória')])
    banco_nome = models.CharField('Banco', max_length=100, blank=True)
    banco_agencia = models.CharField('Agência', max_length=20, blank=True)
    banco_conta = models.CharField('Conta', max_length=30, blank=True)

    # Parâmetros financeiros
    taxa_juros_mes = models.DecimalField('Juros ao mês (%)', max_digits=5, decimal_places=2, default=2)
    percentual_multa = models.DecimalField('Multa por atraso (%)', max_digits=5, decimal_places=2, default=2)
    carencia_juros_dias = models.IntegerField('Dias de carência antes de juros', default=3)
    dias_alerta_vencimento = models.IntegerField('Alertar vencimentos com X dias de antecedência', default=3)

    # Parâmetros de vendas
    vender_sem_estoque = models.BooleanField('Permitir venda com estoque zerado', default=False)
    desconto_maximo = models.DecimalField('Desconto máximo sem senha (%)', max_digits=5, decimal_places=2, default=10)
    forma_pagamento_padrao = models.CharField('Forma de pagamento padrão', max_length=30,
                                               default='DINHEIRO', blank=True)
    imprimir_cupom_auto = models.BooleanField('Imprimir cupom automaticamente', default=False)

    # Configurações de impressão
    cupom_cabecalho = models.TextField('Cabeçalho do cupom', blank=True)
    cupom_rodape = models.TextField('Rodapé do cupom', blank=True,
                                    default='Obrigado pela preferência!\nVolte sempre!')

    # Tema da interface
    tema_cor = models.CharField('Cor principal', max_length=20, default='blue',
                                 choices=[('blue','Azul'),('green','Verde'),('red','Vermelho'),
                                          ('purple','Roxo'),('orange','Laranja'),('teal','Verde-azulado')])
    modo_escuro = models.BooleanField('Modo escuro', default=False)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração da Loja'
        verbose_name_plural = 'Configurações da Loja'

    def __str__(self):
        return f'Configurações — {self.nome_fantasia}'

    def clean(self):
        # Garante que só exista um registro
        if not self.pk and ConfiguracaoLoja.objects.exists():
            raise ValidationError('Já existe uma configuração de loja. Edite a existente.')

    @classmethod
    def get_config(cls):
        """Retorna a configuração única ou cria uma padrão."""
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'nome_fantasia': 'ConfecSystem'})
        return obj
