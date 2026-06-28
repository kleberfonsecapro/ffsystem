import uuid
from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    """
    Model que representa uma transação financeira (receita ou despesa)
    Cada transação pertence a um usuário específico
    """

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
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="tipo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="criado em")

    is_installment = models.BooleanField(default=False, verbose_name="parcelado")
    installment_total = models.IntegerField(null=True, blank=True, verbose_name="total de parcelas")
    installment_number = models.IntegerField(null=True, blank=True, verbose_name="parcela atual")
    installment_group = models.UUIDField(null=True, blank=True, verbose_name="grupo de parcelas")

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        label = f"{self.description} - R$ {self.amount}"
        if self.is_installment:
            label += f" ({self.installment_number}/{self.installment_total})"
        return label
