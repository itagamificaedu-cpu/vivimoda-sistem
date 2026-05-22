from django import forms
from .models import Funcionario, FeriasFuncionario

_ctrl = {'class': 'form-control'}
_sel  = {'class': 'form-select'}

class FormFuncionario(forms.ModelForm):
    class Meta:
        model = Funcionario
        exclude = ['usuario', 'criado_em', 'atualizado_em']
        widgets = {
            'nome_completo': forms.TextInput(attrs={**_ctrl, 'placeholder': 'Nome completo'}),
            'cpf': forms.TextInput(attrs={**_ctrl, 'data-mask': '000.000.000-00'}),
            'rg': forms.TextInput(attrs=_ctrl),
            'data_nascimento': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'sexo': forms.Select(attrs=_sel),
            'estado_civil': forms.Select(attrs=_sel),
            'foto': forms.FileInput(attrs=_ctrl),
            'telefone': forms.TextInput(attrs=_ctrl),
            'celular': forms.TextInput(attrs=_ctrl),
            'email': forms.EmailInput(attrs=_ctrl),
            'cep': forms.TextInput(attrs={**_ctrl, 'id': 'id_cep_func', 'data-mask': '00000-000'}),
            'logradouro': forms.TextInput(attrs=_ctrl),
            'numero': forms.TextInput(attrs=_ctrl),
            'complemento': forms.TextInput(attrs=_ctrl),
            'bairro': forms.TextInput(attrs=_ctrl),
            'cidade': forms.TextInput(attrs=_ctrl),
            'estado': forms.TextInput(attrs={**_ctrl, 'maxlength': '2'}),
            'cargo': forms.TextInput(attrs=_ctrl),
            'setor': forms.TextInput(attrs=_ctrl),
            'salario': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'comissao_percentual': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'data_admissao': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'data_demissao': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'tipo_contrato': forms.Select(attrs=_sel),
            'banco': forms.TextInput(attrs=_ctrl),
            'agencia': forms.TextInput(attrs=_ctrl),
            'conta': forms.TextInput(attrs=_ctrl),
            'tipo_conta': forms.Select(attrs=_sel),
            'pix': forms.TextInput(attrs=_ctrl),
            'ctps_numero': forms.TextInput(attrs=_ctrl),
            'ctps_serie': forms.TextInput(attrs=_ctrl),
            'pis_pasep': forms.TextInput(attrs=_ctrl),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={**_ctrl, 'rows': 3}),
        }


class FormFerias(forms.ModelForm):
    class Meta:
        model = FeriasFuncionario
        fields = ['tipo', 'data_inicio', 'data_fim', 'status', 'observacoes']
        widgets = {
            'tipo': forms.Select(attrs=_sel),
            'data_inicio': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'status': forms.Select(attrs=_sel),
            'observacoes': forms.Textarea(attrs={**_ctrl, 'rows': 2}),
        }
