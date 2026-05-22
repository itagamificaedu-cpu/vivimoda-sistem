"""
Models de autenticação: Usuario customizado, PerfilUsuario, LogAcesso.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """Usuário customizado do sistema."""

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'username']

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def nome_exibicao(self):
        return self.get_full_name() or self.username


class PerfilUsuario(models.Model):
    """Perfil com cargo e permissões por módulo."""

    CARGOS = [
        ('master', 'Master (Dono)'),
        ('gerente', 'Gerente'),
        ('caixa', 'Operador de Caixa'),
        ('estoquista', 'Estoquista'),
        ('financeiro', 'Financeiro'),
    ]

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    cargo = models.CharField('Cargo', max_length=20, choices=CARGOS, default='caixa')
    foto = models.ImageField('Foto', upload_to='usuarios/', blank=True, null=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # Permissões granulares por módulo (True = tem acesso)
    acesso_funcionarios = models.BooleanField('Funcionários', default=False)
    acesso_clientes = models.BooleanField('Clientes', default=True)
    acesso_fornecedores = models.BooleanField('Fornecedores', default=False)
    acesso_produtos = models.BooleanField('Produtos', default=False)
    acesso_estoque = models.BooleanField('Estoque', default=False)
    acesso_compras = models.BooleanField('Compras', default=False)
    acesso_vendas = models.BooleanField('Vendas', default=True)
    acesso_caixa = models.BooleanField('Caixa', default=True)
    acesso_financeiro = models.BooleanField('Financeiro', default=False)
    acesso_carne = models.BooleanField('Carnê', default=True)
    acesso_relatorios = models.BooleanField('Relatórios', default=False)
    acesso_configuracoes = models.BooleanField('Configurações', default=False)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f'{self.usuario} — {self.get_cargo_display()}'

    def tem_acesso(self, modulo: str) -> bool:
        """Verifica se o perfil tem acesso ao módulo. Master tem acesso total."""
        if self.cargo == 'master':
            return True
        return getattr(self, f'acesso_{modulo}', False)


class LogAcesso(models.Model):
    """Auditoria de todas as ações do sistema."""

    ACOES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('CRIAR', 'Criar'),
        ('EDITAR', 'Editar'),
        ('EXCLUIR', 'Excluir'),
        ('VISUALIZAR', 'Visualizar'),
        ('EXPORTAR', 'Exportar'),
        ('IMPRIMIR', 'Imprimir'),
        ('CANCELAR', 'Cancelar'),
        ('BAIXAR', 'Baixar Pagamento'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, verbose_name='Usuário')
    acao = models.CharField('Ação', max_length=20, choices=ACOES)
    modelo = models.CharField('Modelo', max_length=100, blank=True)
    objeto_id = models.CharField('ID do Objeto', max_length=50, blank=True)
    descricao = models.TextField('Descrição', blank=True)
    ip = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    criado_em = models.DateTimeField('Data/Hora', auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'criado_em']),
            models.Index(fields=['modelo', 'objeto_id']),
        ]

    def __str__(self):
        return f'{self.usuario} — {self.acao} — {self.criado_em.strftime("%d/%m/%Y %H:%M")}'


class TentativaLogin(models.Model):
    """Controla bloqueio após tentativas falhas de login."""

    username = models.CharField('Usuário', max_length=150)
    ip = models.GenericIPAddressField('IP')
    tentativas = models.IntegerField('Tentativas', default=0)
    bloqueado_ate = models.DateTimeField('Bloqueado até', null=True, blank=True)
    ultima_tentativa = models.DateTimeField('Última tentativa', auto_now=True)

    class Meta:
        verbose_name = 'Tentativa de Login'
        verbose_name_plural = 'Tentativas de Login'
        unique_together = [['username', 'ip']]

    def __str__(self):
        return f'{self.username} ({self.ip}) — {self.tentativas} tentativas'

    def esta_bloqueado(self) -> bool:
        if self.bloqueado_ate and self.bloqueado_ate > timezone.now():
            return True
        return False

    def registrar_falha(self, max_tentativas=5, minutos_bloqueio=30):
        from datetime import timedelta
        self.tentativas += 1
        if self.tentativas >= max_tentativas:
            self.bloqueado_ate = timezone.now() + timedelta(minutes=minutos_bloqueio)
        self.save()

    def resetar(self):
        self.tentativas = 0
        self.bloqueado_ate = None
        self.save()
