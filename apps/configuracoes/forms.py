from django import forms
from .models import ConfiguracaoLoja


class FormConfiguracaoLoja(forms.ModelForm):
    class Meta:
        model = ConfiguracaoLoja
        exclude = ['criado_em', 'atualizado_em']
        widgets = {
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'inscricao_estadual': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cep'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'site': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
            'pix_chave': forms.TextInput(attrs={'class': 'form-control'}),
            'pix_tipo': forms.Select(attrs={'class': 'form-select'}),
            'banco_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'banco_agencia': forms.TextInput(attrs={'class': 'form-control'}),
            'banco_conta': forms.TextInput(attrs={'class': 'form-control'}),
            'taxa_juros_mes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'percentual_multa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'carencia_juros_dias': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_alerta_vencimento': forms.NumberInput(attrs={'class': 'form-control'}),
            'desconto_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'forma_pagamento_padrao': forms.Select(attrs={'class': 'form-select'}),
            'cupom_cabecalho': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cupom_rodape': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tema_cor': forms.Select(attrs={'class': 'form-select'}),
        }
