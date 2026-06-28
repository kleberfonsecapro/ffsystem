from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User


class CadastroForm(UserCreationForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Escolha um nome de usuário"}),
    )
    email = forms.EmailField(
        label="E-mail",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "seu@email.com"}),
    )
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Crie uma senha"}),
    )
    password2 = forms.CharField(
        label="Confirmação de senha",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Repita a senha"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = (
            "Sua senha deve conter pelo menos 8 caracteres."
        )
        self.fields["password2"].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class AlterarSenhaForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Digite sua senha atual"}),
    )
    new_password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Digite a nova senha"}),
    )
    new_password2 = forms.CharField(
        label="Confirmação da nova senha",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Repita a nova senha"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = (
            "Sua senha deve conter pelo menos 8 caracteres. "
            "Não pode ser muito parecida com suas outras informações pessoais, "
            "nem ser uma senha comum ou totalmente numérica."
        )
