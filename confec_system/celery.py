"""
Configuração do Celery para tarefas assíncronas e agendamentos.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'confec_system.settings.development')

app = Celery('confec_system')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover de tarefas em todos os apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
