"""
Admin de Funcionários.
"""
from django.contrib import admin
from .models import Funcionario, HistoricoSalario, FeriasFuncionario


class HistoricoSalarioInline(admin.TabularInline):
    model = HistoricoSalario
    extra = 0
    readonly_fields = ['salario_anterior', 'salario_novo', 'motivo', 'data_alteracao', 'usuario']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class FeriasInline(admin.TabularInline):
    model = FeriasFuncionario
    extra = 0
    fields = ['tipo', 'data_inicio', 'data_fim', 'dias', 'status', 'observacoes']
    readonly_fields = ['dias']


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = [
        'nome_completo', 'cpf', 'cargo', 'setor', 'salario',
        'data_admissao', 'tipo_contrato', 'ativo',
    ]
    list_filter = ['ativo', 'tipo_contrato', 'cargo', 'setor']
    search_fields = ['nome_completo', 'cpf', 'cargo', 'email', 'celular']
    ordering = ['nome_completo']
    inlines = [HistoricoSalarioInline, FeriasInline]
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'cpf', 'rg', 'data_nascimento', 'sexo', 'estado_civil', 'foto')
        }),
        ('Contato', {
            'fields': ('telefone', 'celular', 'email')
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Dados Profissionais', {
            'fields': ('cargo', 'setor', 'salario', 'comissao_percentual',
                       'data_admissao', 'data_demissao', 'tipo_contrato')
        }),
        ('Dados Bancários', {
            'fields': ('banco', 'agencia', 'conta', 'tipo_conta', 'pix'),
            'classes': ('collapse',),
        }),
        ('Documentos', {
            'fields': ('ctps_numero', 'ctps_serie', 'pis_pasep'),
            'classes': ('collapse',),
        }),
        ('Sistema', {
            'fields': ('usuario', 'ativo', 'observacoes', 'criado_em', 'atualizado_em')
        }),
    )


@admin.register(FeriasFuncionario)
class FeriasAdmin(admin.ModelAdmin):
    list_display = ['funcionario', 'tipo', 'data_inicio', 'data_fim', 'dias', 'status']
    list_filter = ['tipo', 'status', 'data_inicio']
    search_fields = ['funcionario__nome_completo']
    ordering = ['-data_inicio']
