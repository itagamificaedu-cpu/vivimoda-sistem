"""
Management command: carregar_fixtures
Carrega todos os dados demo e configura usuarios com senhas corretas.

Uso:
    python manage.py carregar_fixtures
"""
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__),  # .../apps/core/management/commands/
    '..', '..', '..', '..',    # sobe 4 niveis -> raiz do projeto (confec_system/)
    'fixtures'
)

# Ordem de carga respeita dependencias de FK
FIXTURE_FILES = [
    '01_categorias.json',
    '02_marcas_cores_tamanhos.json',
    '03_produtos.json',
    '04_clientes.json',
    '05_usuarios.json',
    '06_fornecedores.json',
    '07_financeiro_base.json',
    '08_caixa.json',
    '09_configuracoes.json',
]

# Usuarios demo e suas senhas
SENHAS_DEMO = {
    'admin':   'confec@2024',
    'gerente': 'gerente@2024',
    'caixa1':  'caixa@2024',
}


class Command(BaseCommand):
    help = 'Carrega dados demo do ConfecSystem (fixtures + senhas corretas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Apaga dados existentes antes de carregar (use com cautela!)',
        )

    def handle(self, *args, **options):
        self.stdout.write('\n=== ConfecSystem - Carregando dados demo ===\n')

        # 1. Carrega cada fixture
        fixtures_path = os.path.normpath(FIXTURES_DIR)
        self.stdout.write(f'Diretorio de fixtures: {fixtures_path}\n')

        for nome in FIXTURE_FILES:
            caminho = os.path.join(fixtures_path, nome)
            if not os.path.exists(caminho):
                self.stdout.write(f'  [SKIP] {nome} - arquivo nao encontrado')
                continue
            try:
                call_command('loaddata', caminho, verbosity=0)
                self.stdout.write(self.style.SUCCESS(f'  [OK]   {nome}'))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'  [ERRO] {nome}: {exc}'))

        # 2. Corrige as senhas dos usuarios demo
        self.stdout.write('\nDefinindo senhas dos usuarios demo...')
        from apps.autenticacao.models import Usuario

        with transaction.atomic():
            for username, senha in SENHAS_DEMO.items():
                try:
                    usuario = Usuario.objects.get(username=username)
                    usuario.set_password(senha)
                    usuario.save(update_fields=['password'])
                    self.stdout.write(self.style.SUCCESS(f'  [OK]   {username} => senha definida'))
                except Usuario.DoesNotExist:
                    self.stdout.write(f'  [SKIP] Usuario {username!r} nao existe')

        # 3. Cria configuracao padrao da loja
        self.stdout.write('\nCriando configuracao padrao da loja...')
        try:
            from apps.configuracoes.models import ConfiguracaoLoja
            config, criado = ConfiguracaoLoja.objects.get_or_create(pk=1, defaults={
                'nome_loja': 'VIVIMODA',
                'razao_social': 'VIVIMODA Comercio de Confeccoes Ltda',
                'cnpj': '00.000.000/0001-00',
                'telefone': '(11) 99999-0000',
                'email': 'contato@vivimoda.com.br',
                'cidade': 'Sao Paulo',
                'estado': 'SP',
                'taxa_juros_mes': '2.00',
                'percentual_multa': '2.00',
                'carencia_juros_dias': 3,
                'prazo_maximo_carne': 12,
                'estoque_minimo_alerta': True,
            })
            if criado:
                self.stdout.write(self.style.SUCCESS('  [OK]   Configuracao criada'))
            else:
                self.stdout.write('  [SKIP] Configuracao ja existe')
        except Exception as exc:
            self.stdout.write(f'  [SKIP] ConfiguracaoLoja: {exc}')

        # 4. Cria caixa padrao
        self.stdout.write('\nCriando caixa padrao...')
        try:
            from apps.caixa.models import Caixa
            caixa, criado = Caixa.objects.get_or_create(numero='01', defaults={
                'descricao': 'Caixa Principal',
                'ativo': True,
            })
            if criado:
                self.stdout.write(self.style.SUCCESS('  [OK]   Caixa 01 criado'))
            else:
                self.stdout.write('  [SKIP] Caixa 01 ja existe')
        except Exception as exc:
            self.stdout.write(f'  [SKIP] Caixa: {exc}')

        # 5. Registra tarefas no Celery Beat
        self.stdout.write('\nRegistrando tarefas agendadas (Celery Beat)...')
        _registrar_tasks_celery_beat(self)

        self.stdout.write(self.style.SUCCESS('\n[OK] Dados demo carregados com sucesso!\n'))
        self.stdout.write('Credenciais de acesso:')
        self.stdout.write('  admin   => confec@2024   (superusuario)')
        self.stdout.write('  gerente => gerente@2024  (gerente)')
        self.stdout.write('  caixa1  => caixa@2024    (operador de caixa)')


def _registrar_tasks_celery_beat(command):
    """Registra as tarefas periodicas no django-celery-beat."""
    try:
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        import json

        tarefas = [
            # (minuto, hora, nome, task)
            ('1',  '0', 'Marcar Parcelas Vencidas',   'carne.marcar_parcelas_vencidas'),
            ('5',  '0', 'Marcar Contas Vencidas',     'financeiro.marcar_contas_vencidas'),
            ('10', '0', 'Calcular Juros Automatico',  'financeiro.calcular_juros_automatico'),
            ('15', '0', 'Atualizar Status Vendas',    'core.atualizar_status_vendas'),
            ('0',  '3', 'Limpar Sessoes Expiradas',   'core.limpar_sessoes_expiradas'),
            ('0',  '6', 'Relatorio Diario',            'core.relatorio_diario'),
            ('0',  '8', 'Notificar Vencimentos',       'carne.notificar_vencimentos_proximos'),
        ]

        criadas = 0
        for minuto, hora, nome, task in tarefas:
            crontab, _ = CrontabSchedule.objects.get_or_create(
                minute=minuto, hour=hora,
                day_of_week='*', day_of_month='*', month_of_year='*',
            )
            _, criado = PeriodicTask.objects.get_or_create(
                name=nome,
                defaults={
                    'crontab': crontab,
                    'task': task,
                    'args': json.dumps([]),
                    'enabled': True,
                }
            )
            if criado:
                criadas += 1

        command.stdout.write(command.style.SUCCESS(f'  [OK]   {criadas} tarefas registradas no Celery Beat'))

    except ImportError:
        command.stdout.write(
            '  [SKIP] django-celery-beat nao instalado (execute: pip install django-celery-beat)'
        )
    except Exception as exc:
        command.stdout.write(f'  [SKIP] Celery Beat: {exc}')
