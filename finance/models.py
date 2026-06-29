import uuid
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    TYPE_CHOICES = [
        ("receita", "Receita"),
        ("despesa", "Despesa"),
        ("ambos", "Ambos"),
    ]

    name = models.CharField(max_length=100, verbose_name="nome")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="usuário")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="ambos", verbose_name="tipo")

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TYPE_CHOICES = [
        ("receita", "Receita"),
        ("despesa", "Despesa"),
    ]

    CATEGORY_CHOICES = [
        ("Salário", "Salário"),
        ("Alimentação", "Alimentação"),
        ("Transporte", "Transporte"),
        ("Lazer", "Lazer"),
        ("Moradia", "Moradia"),
        ("Saúde", "Saúde"),
        ("Educação", "Educação"),
        ("Outros", "Outros"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="usuário")
    description = models.CharField(max_length=255, verbose_name="descrição")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="valor")
    date = models.DateField(verbose_name="data")
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, verbose_name="categoria")
    category_ref = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="categoria (ref)")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="tipo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    paid = models.BooleanField(default=False, verbose_name="paga")
    is_installment = models.BooleanField(default=False, verbose_name="parcelado")
    installment_total = models.IntegerField(null=True, blank=True, verbose_name="total de parcelas")
    installment_number = models.IntegerField(null=True, blank=True, verbose_name="parcela atual")
    installment_group = models.UUIDField(null=True, blank=True, verbose_name="grupo de parcelas")

    class Meta:
        verbose_name = "transação"
        verbose_name_plural = "transações"
        ordering = ["-date", "-created_at"]

    @property
    def category_display(self):
        return self.category_ref.name if self.category_ref_id else self.category

    def save(self, *args, **kwargs):
        if self.category_ref_id:
            self.category = self.category_ref.name
        super().save(*args, **kwargs)

    def __str__(self):
        label = f"{self.description} - R$ {self.amount}"
        if self.is_installment:
            label += f" ({self.installment_number}/{self.installment_total})"
        return label


class TransactionDocument(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="documents", verbose_name="transação")
    file = models.FileField(upload_to="documents/%Y/%m/%d/", verbose_name="arquivo")
    filename_original = models.CharField(max_length=255, verbose_name="nome original")
    filesize = models.IntegerField(verbose_name="tamanho (bytes)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="enviado em")

    class Meta:
        verbose_name = "documento"
        verbose_name_plural = "documentos"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.filename_original
