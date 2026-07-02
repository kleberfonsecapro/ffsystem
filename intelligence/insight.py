import logging
from datetime import date, timedelta

from django.db.models import Sum

from .groq_client import get_groq_client
from .rate_limiter import check_groq_rate_limit

logger = logging.getLogger(__name__)


def generate_insight(user):
    from finance.models import Transaction

    client = get_groq_client()
    today = date.today()
    month_start = today.replace(day=1)

    transactions = Transaction.objects.filter(user=user)

    if not transactions.exists():
        return "Registre suas primeiras transações para receber insights."

    month_income = transactions.filter(
        type="receita", date__gte=month_start, date__lte=today
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    month_expense = transactions.filter(
        type="despesa", date__gte=month_start, date__lte=today
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    balance = month_income - month_expense

    prev_month_end = month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)

    prev_income = transactions.filter(
        type="receita", date__gte=prev_month_start, date__lte=prev_month_end
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    prev_expense = transactions.filter(
        type="despesa", date__gte=prev_month_start, date__lte=prev_month_end
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    categories = (
        transactions.filter(date__gte=month_start, date__lte=today)
        .values("category_ref__name", "type")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    expense_cats = [c for c in categories if c["type"] == "despesa"]
    income_cats = [c for c in categories if c["type"] == "receita"]

    def fmt_cats(cats, label):
        if not cats:
            return "  Nenhuma"
        return "\n".join(
            f"  - {c['category_ref__name'] or label}: R$ {c['total']:.2f}"
            for c in cats[:5]
        )

    expense_text = fmt_cats(expense_cats, "Sem categoria")
    income_text = fmt_cats(income_cats, "Sem categoria")

    if not client:
        return _fallback_insight(month_income, month_expense, balance)

    if not check_groq_rate_limit(user.pk, limit=6, window=60, scope="insight"):
        return _fallback_insight(month_income, month_expense, balance)

    prompt = f"""Você é um analista financeiro pessoal. Analise os dados abaixo e gere UM parágrafo curto (máximo 80 palavras) com um insight útil e personalizado.

Mês: {today.strftime('%B/%Y')}
Receitas: R$ {month_income:.2f}
Despesas: R$ {month_expense:.2f}
Saldo: R$ {balance:.2f}
Mês anterior - Receitas: R$ {prev_income:.2f} | Despesas: R$ {prev_expense:.2f}

Top despesas:
{expense_text}

Top receitas:
{income_text}

Regras: Seja direto. Destaque o maior gasto. Compare com mês anterior. Dê uma dica prática. Responda em português brasileiro natural. Não use listas ou marcadores."""

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um analista financeiro que gera insights curtos e práticos em português.",
                },
                {"role": "user", "content": prompt},
            ],
            model="llama-3.1-8b-instant",
            timeout=30,
        )

        insight = response.choices[0].message.content.strip().strip('"')
        logger.info("Insight gerado via IA para usuário %s", user)
        return insight

    except Exception as e:
        logger.exception(
            "Erro ao gerar insight via IA para usuário %s. Usando fallback.", user
        )
        return _fallback_insight(month_income, month_expense, balance)


def _fallback_insight(month_income, month_expense, balance):
    if month_expense == 0:
        return "Sem despesas este mês. Aproveite para planejar seus próximos gastos!"

    if month_expense > month_income:
        deficit = month_expense - month_income
        return (
            f"Atenção: suas despesas superaram as receitas em R$ {deficit:.2f} "
            f"este mês. Reveja gastos não essenciais para equilibrar as contas."
        )

    pct = (month_expense / month_income) * 100
    if pct > 80:
        return (
            f"Você gastou {pct:.1f}% das receitas. Saldo positivo de "
            f"R$ {balance:.2f}, mas a margem está apertada. Tente poupar mais."
        )

    return (
        f"No mês você gastou {pct:.1f}% das receitas. "
        f"Saldo positivo de R$ {balance:.2f}. Continue assim!"
    )
