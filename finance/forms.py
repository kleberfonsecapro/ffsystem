import os
from django import forms
from .models import Transaction, Category, TransactionDocument


class TransactionForm(forms.ModelForm):
    """Form for manual transaction entry (manual entry, not parcelamento)"""
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
        fields = [
            "description",
            "amount",
            "date",
            "category_ref",
            "type",
            "is_installment",
            "installment_total",
        ]
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
        self.fields["category_ref"].queryset = (
            Category.objects.filter(user__isnull=True)
            | Category.objects.filter(user=self.instance.user if self.instance.pk else None)
        )
        self.fields["category_ref"].empty_label = None

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
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


class CSVImportForm(forms.Form):
    file = forms.FileField(
        label="Arquivo CSV",
        help_text=(
            "Envie arquivo .csv delimitado por ponto e vírgula (;) "
            "com cabeçalho: Data;Descrição;Categoria;Tipo;Valor;Parcela;Paga."
        ),
    )

    def clean_file(self):
        csv_file = self.cleaned_data["file"]
        if not csv_file.name.lower().endswith(".csv"):
            raise forms.ValidationError("Envie um arquivo CSV com extensão .csv.")

        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError("O arquivo CSV deve ter no máximo 5 MB.")

        sample = csv_file.read(2048)
        csv_file.seek(0)

        try:
            sample_text = sample.decode("utf-8")
        except UnicodeDecodeError:
            raise forms.ValidationError("O arquivo deve estar codificado em UTF-8.")

        if ";" not in sample_text:
            raise forms.ValidationError("Use ponto e vírgula (;) como delimitador no CSV.")

        return csv_file


class TransactionDocumentForm(forms.ModelForm):
    class Meta:
        model = TransactionDocument
        fields = ["file"]
        labels = {"file": "Comprovante"}
        help_texts = {"file": "PDF, JPEG ou PNG. Máximo 10 MB."}
        widgets = {"file": forms.ClearableFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"})}

    ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
    MAX_SIZE = 10 * 1024 * 1024

    def clean_file(self):
        f = self.cleaned_data["file"]
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Formato não suportado. Use PDF, JPEG ou PNG.")
        if f.size > self.MAX_SIZE:
            raise forms.ValidationError("O arquivo deve ter no máximo 10 MB.")
        return f
