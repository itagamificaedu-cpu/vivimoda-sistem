from django import forms
from .models import LancamentoFinanceiro, ContaBancaria, PlanoContas

_ctrl = {'class': 'form-control'}
_sel  = {'class': 'form-select'}

class FormLancamento(forms.ModelForm):
    class Meta:
        model = LancamentoFinanceiro
        exclude = ['usuario', 'criado_em']
        widgets = {
            'tipo': forms.Select(attrs=_sel),
            'plano_contas': forms.Select(attrs=_sel),
            'descricao': forms.TextInput(attrs=_ctrl),
            'valor': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'data_competencia': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'data_pagamento': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'status': forms.Select(attrs=_sel),
            'conta_bancaria': forms.Select(attrs=_sel),
            'recorrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recorrencia': forms.Select(attrs=_sel),
            'anexo': forms.FileInput(attrs=_ctrl),
            'observacoes': forms.Textarea(attrs={**_ctrl, 'rows': 2}),
        }

class FormContaBancaria(forms.ModelForm):
    class Meta:
        model = ContaBancaria
        exclude = []
        widgets = {
            'nome': forms.TextInput(attrs=_ctrl),
            'banco': forms.TextInput(attrs=_ctrl),
            'agencia': forms.TextInput(attrs=_ctrl),
            'conta': forms.TextInput(attrs=_ctrl),
            'tipo': forms.Select(attrs=_sel),
            'saldo_inicial': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'saldo_atual': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
