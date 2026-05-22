"""
Management command: criar_admin (apps.core)
Delegado ao comando equivalente em apps.autenticacao para manter compatibilidade.
O comando real está em apps/autenticacao/management/commands/criar_admin.py.

Como apps.core vem antes de apps.autenticacao no INSTALLED_APPS, este é o comando
que o Django encontra primeiro, então implementamos a lógica completa aqui.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria o superusuário padrão admin/confec@2024 (idempotente)'

    def handle(self, *args, **options):
        from apps.autenticacao.models import Usuario

        username = 'admin'
        senha = 'confec@2024'
        email = 'admin@vivimoda.com.br'

        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Usuário {username!r} já existe — nenhuma alteração feita.')
            )
            return

        # create_superuser dispara o signal que cria o PerfilUsuario automaticamente
        Usuario.objects.create_superuser(
            username=username,
            email=email,
            password=senha,
            first_name='Administrador',
            last_name='Sistema',
        )

        self.stdout.write(self.style.SUCCESS('OK Superusuario criado: admin / confec@2024'))
        self.stdout.write(f'  Login:  {username}')
        self.stdout.write(f'  Senha:  {senha}')
        self.stdout.write(f'  E-mail: {email}')
