from django import forms
from .models import Transaction, Category


class TransactionForm(forms.ModelForm):
    is_installment = forms.BooleanField(
        required=False,
        label="Pagamento parcelado",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "id": "id_is_installment"}),
    )
    installment_total = forms.IntegerField(
        required=False,
        label="Número de parcelas",
        min_value=2,
        max_value=120,
        widget=forms.NumberInput(attrs={
            "class": "form-control", "placeholder": "Ex: 12", "id": "id_installment_total",
        }),
    )

    class Meta:
        model = Transaction
        fields = ["description", "amount", "date", "category_ref", "type"]
        labels = {
            "description": "Descrição",
            "amount": "Valor (R$)",
            "date": "Data",
            "category_ref": "Categoria",
            "type": "Tipo",
        }
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Salário, Mercado..."}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "0.00"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "category_ref": forms.Select(attrs={"class": "form-control"}),
            "type": forms.RadioSelect(attrs={"class": "type-radio"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category_ref"].queryset = Category.objects.filter(
            user__isnull=True
        ) | Category.objects.filter(user=self.instance.user if self.instance.pk else None)
        self.fields["category_ref"].empty_label = None

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return amount

    def clean(self):
        cleaned = super().clean()
        is_installment = cleaned.get("is_installment")
        installment_total = cleaned.get("installment_total")

        if is_installment:
            if not installment_total or installment_total < 2:
                self.add_error("installment_total", "Informe o número de parcelas (mínimo 2).")
        return cleaned
