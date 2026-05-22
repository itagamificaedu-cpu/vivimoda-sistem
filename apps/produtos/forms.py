from django import forms
from .models import Produto, GradeProduto, Categoria, SubCategoria, Marca

_ctrl = {'class': 'form-control'}
_sel  = {'class': 'form-select'}

class FormProduto(forms.ModelForm):
    class Meta:
        model = Produto
        exclude = ['criado_em', 'atualizado_em']
        widgets = {
            'codigo': forms.TextInput(attrs={**_ctrl, 'placeholder': 'Gerado automaticamente se vazio'}),
            'codigo_barras': forms.TextInput(attrs=_ctrl),
            'referencia': forms.TextInput(attrs=_ctrl),
            'nome': forms.TextInput(attrs={**_ctrl, 'placeholder': 'Nome do produto'}),
            'descricao': forms.Textarea(attrs={**_ctrl, 'rows': 3}),
            'categoria': forms.Select(attrs=_sel),
            'subcategoria': forms.Select(attrs=_sel),
            'marca': forms.Select(attrs=_sel),
            'tipo': forms.Select(attrs=_sel),
            'preco_custo': forms.NumberInput(attrs={**_ctrl, 'step': '0.01', 'id': 'id_preco_custo'}),
            'margem_lucro': forms.NumberInput(attrs={**_ctrl, 'step': '0.01', 'id': 'id_margem_lucro'}),
            'preco_venda': forms.NumberInput(attrs={**_ctrl, 'step': '0.01', 'id': 'id_preco_venda'}),
            'preco_promocional': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'promocao_inicio': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'promocao_fim': forms.DateInput(attrs={**_ctrl, 'type': 'date'}),
            'estoque_atual': forms.NumberInput(attrs={**_ctrl, 'step': '0.001'}),
            'estoque_minimo': forms.NumberInput(attrs={**_ctrl, 'step': '0.001'}),
            'estoque_maximo': forms.NumberInput(attrs={**_ctrl, 'step': '0.001'}),
            'unidade': forms.TextInput(attrs=_ctrl),
            'localizacao': forms.TextInput(attrs=_ctrl),
            'ncm': forms.TextInput(attrs=_ctrl),
            'cest': forms.TextInput(attrs=_ctrl),
            'cfop': forms.TextInput(attrs=_ctrl),
            'origem': forms.Select(attrs=_sel),
            'foto_principal': forms.FileInput(attrs=_ctrl),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FormGrade(forms.ModelForm):
    class Meta:
        model = GradeProduto
        exclude = ['produto']
        widgets = {
            'cor': forms.Select(attrs=_sel),
            'tamanho': forms.Select(attrs=_sel),
            'codigo_barras': forms.TextInput(attrs=_ctrl),
            'preco_adicional': forms.NumberInput(attrs={**_ctrl, 'step': '0.01'}),
            'estoque_atual': forms.NumberInput(attrs={**_ctrl, 'step': '0.001'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FormCategoria(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs=_ctrl),
            'descricao': forms.Textarea(attrs={**_ctrl, 'rows': 2}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
