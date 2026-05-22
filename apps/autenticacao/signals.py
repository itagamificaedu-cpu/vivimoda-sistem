"""
Signals — cria PerfilUsuario automaticamente ao criar novo usuário.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Usuario, PerfilUsuario


@receiver(post_save, sender=Usuario)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    """Cria perfil com cargo padrão 'caixa' para todo novo usuário."""
    if created:
        cargo = 'master' if instance.is_superuser else 'caixa'
        PerfilUsuario.objects.get_or_create(
            usuario=instance,
            defaults={'cargo': cargo}
        )
