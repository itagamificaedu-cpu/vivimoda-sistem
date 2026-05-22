"""
Comando para criar o superusuário padrão do sistema.
"""
from django.core.management.base import BaseCommand
from apps.autenticacao.models import Usuario, PerfilUsuario


class Command(BaseCommand):
    help = 'Cria o superusuário padrão: admin / confec@2024'

    def handle(self, *args, **kwargs):
        if Usuario.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Usuário admin já existe. Pulando criação.'))
            return

        usuario = Usuario.objects.create_superuser(
            username='admin',
            email='admin@confec.com',
            password='confec@2024',
            first_name='Administrador',
            last_name='Master',
        )

        PerfilUsuario.objects.filter(usuario=usuario).update(
            cargo='master',
            acesso_funcionarios=True,
            acesso_clientes=True,
            acesso_fornecedores=True,
            acesso_produtos=True,
            acesso_estoque=True,
            acesso_compras=True,
            acesso_vendas=True,
            acesso_caixa=True,
            acesso_financeiro=True,
            acesso_carne=True,
            acesso_relatorios=True,
            acesso_configuracoes=True,
        )

        self.stdout.write(self.style.SUCCESS('✓ Superusuário criado: admin / confec@2024'))
