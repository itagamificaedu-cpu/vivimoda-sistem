"""
Formulários de autenticação.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import Usuario, PerfilUsuario


class FormLogin(AuthenticationForm):
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome de usuário',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Senha',
        })
    )


class FormTrocarSenha(PasswordChangeForm):
    old_password = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirme a nova senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class FormPerfilUsuario(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['foto', 'cargo',
                  'acesso_funcionarios', 'acesso_clientes', 'acesso_fornecedores',
                  'acesso_produtos', 'acesso_estoque', 'acesso_compras',
                  'acesso_vendas', 'acesso_caixa', 'acesso_financeiro',
                  'acesso_carne', 'acesso_relatorios', 'acesso_configuracoes']
        widgets = {
            'cargo': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FormCriarUsuario(forms.ModelForm):
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=6
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        s1 = cleaned.get('senha')
        s2 = cleaned.get('confirmar_senha')
        if s1 and s2 and s1 != s2:
            raise forms.ValidationError('As senhas não coincidem.')
        return cleaned

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['senha'])
        if commit:
            usuario.save()
        return usuario
