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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.description} - R$ {self.amount}"
