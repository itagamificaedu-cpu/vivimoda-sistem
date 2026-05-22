from django import forms
from .models import Cliente

_ctrl = {'class': 'form-control'}
_sel  = {'class': 'form-select'}

class FormCliente(forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = ['saldo_devedor', 'pontos_fidelidade', 'criado_em', 'atualizado_em']
        widgets = {
            'tipo': forms.Select(attrs=_sel),
            'nome': forms.TextInput(attrs=_ctrl),
            'cpf': forms.TextInput(attrs={**_ctrl, 'data-mask': '000.000.000-00'}),
            'rg': forms.TextInput(attrs=_ctrl),
            'data_nascimento': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'sexo': forms.Select(attrs=_sel),
            'razao_social': forms.TextInput(attrs=_ctrl),
            'cnpj': forms.TextInput(attrs={**_ctrl, 'data-mask': '00.000.000/0000-00'}),
            'inscricao_estadual': forms.TextInput(attrs=_ctrl),
            'nome_fantasia': forms.TextInput(attrs=_ctrl),
            'telefone': forms.TextInput(attrs=_ctrl),
            'celular': forms.TextInput(attrs=_ctrl),
            'whatsapp': forms.TextInput(attrs=_ctrl),
            'email': forms.EmailInput(attrs=_ctrl),
            'cep': forms.TextInput(attrs={**_ctrl, 'id': 'id_cep_cliente'}),
            'logradouro': forms.TextInput(attrs=_ctrl),
            'numero': forms.TextInput(attrs=_ctrl),
            'complemento': forms.TextInput(attrs=_ctrl),
            'bairro': forms.TextInput(attrs=_ctrl),
            'cidade': forms.TextInput(attrs=_ctrl),
            'estado': forms.TextInput(attrs={**_ctrl, 'maxlength': '2'}),
            'limite_credito': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'dia_vencimento': forms.NumberInput(attrs={**_ctrl, 'min': '1', 'max': '28'}),
            'categoria': forms.Select(attrs=_sel),
            'foto': forms.FileInput(attrs=_ctrl),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={**_ctrl, 'rows': 3}),
        }
