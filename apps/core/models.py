"""
Modelos base abstratos para reuso em todo o sistema.
"""
from django.db import models


class ModeloBase(models.Model):
    """Modelo base com timestamps automáticos."""
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        abstract = True


class ModeloBaseUsuario(ModeloBase):
    """Modelo base com timestamps e usuário responsável."""
    usuario = models.ForeignKey(
        'autenticacao.Usuario',
        on_delete=models.PROTECT,
        verbose_name='Usuário',
        related_name='+'
    )

    class Meta:
        abstract = True
