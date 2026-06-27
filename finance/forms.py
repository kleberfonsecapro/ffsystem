from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["description", "amount", "date", "category", "type"]
        labels = {
            "description": "Descrição",
            "amount": "Valor (R$)",
            "date": "Data",
            "category": "Categoria",
            "type": "Tipo",
        }
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Salário, Mercado..."}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "type": forms.RadioSelect(attrs={"class": "type-radio"}),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return amount
