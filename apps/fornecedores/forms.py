from django import forms
from .models import Fornecedor, ContatoFornecedor

_ctrl = {'class': 'form-control'}
_sel  = {'class': 'form-select'}

class FormFornecedor(forms.ModelForm):
    class Meta:
        model = Fornecedor
        exclude = ['criado_em', 'atualizado_em']
        widgets = {
            'tipo': forms.Select(attrs=_sel),
            'razao_social': forms.TextInput(attrs=_ctrl),
            'nome_fantasia': forms.TextInput(attrs=_ctrl),
            'cnpj': forms.TextInput(attrs={**_ctrl, 'data-mask': '00.000.000/0000-00'}),
            'cpf': forms.TextInput(attrs={**_ctrl, 'data-mask': '000.000.000-00'}),
            'inscricao_estadual': forms.TextInput(attrs=_ctrl),
            'telefone': forms.TextInput(attrs=_ctrl),
            'celular': forms.TextInput(attrs=_ctrl),
            'email': forms.EmailInput(attrs=_ctrl),
            'site': forms.URLInput(attrs=_ctrl),
            'cep': forms.TextInput(attrs={**_ctrl, 'id': 'id_cep_forn'}),
            'logradouro': forms.TextInput(attrs=_ctrl),
            'numero': forms.TextInput(attrs=_ctrl),
            'complemento': forms.TextInput(attrs=_ctrl),
            'bairro': forms.TextInput(attrs=_ctrl),
            'cidade': forms.TextInput(attrs=_ctrl),
            'estado': forms.TextInput(attrs={**_ctrl, 'maxlength': '2'}),
            'prazo_pagamento': forms.NumberInput(attrs=_ctrl),
            'condicao_pagamento': forms.TextInput(attrs=_ctrl),
            'desconto_padrao': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'avaliacao': forms.Select(attrs=_sel),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={**_ctrl, 'rows': 3}),
        }

class FormContatoFornecedor(forms.ModelForm):
    class Meta:
        model = ContatoFornecedor
        fields = ['nome', 'cargo', 'celular', 'email', 'principal']
        widgets = {
            'nome': forms.TextInput(attrs=_ctrl),
            'cargo': forms.TextInput(attrs=_ctrl),
            'celular': forms.TextInput(attrs=_ctrl),
            'email': forms.EmailInput(attrs=_ctrl),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
