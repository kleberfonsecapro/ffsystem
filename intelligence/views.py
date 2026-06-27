import os
import json
import logging
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from groq import Groq
from finance.models import Transaction

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {"Salário", "Alimentação", "Transporte", "Lazer", "Moradia", "Saúde", "Educação", "Outros"}
VALID_TYPES = {"receita", "despesa"}


@login_required(login_url="/users/login/")
def chat_view(request):
    return render(request, "chat.html")


@login_required(login_url="/users/login/")
@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        user_message = data.get("message", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not user_message:
        return JsonResponse({"error": "Mensagem vazia"}, status=400)

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("Tentativa de uso do chat IA sem GROQ_API_KEY configurada")
        return JsonResponse({"reply": "Assistente IA não configurado. Contate o administrador."})

    today = date.today().isoformat()

    system_prompt = f"""
Você é SmartFinance AI, assistente financeiro.
Se reconhecer um registro financeiro (gasto/ganho), retorne JSON:
{{"is_transaction": true, "amount": 100.50, "date": "{today}",
 "category": "Alimentação", "type": "despesa", "description": "Comida"}}
Se NÃO for transação:
"is_transaction": false, "reply": "sua resposta"
IMPORTANTE: Apenas retorne JSON válido. Não invente dados.
"""

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            timeout=30,
        )

        raw = response.choices[0].message.content
        result = json.loads(raw)

        if result.get("is_transaction"):
            errors = []
            amount_raw = result.get("amount")
            try:
                amount = Decimal(str(amount_raw))
                if amount <= 0:
                    errors.append("Valor deve ser positivo")
            except (InvalidOperation, TypeError, ValueError):
                errors.append("Valor inválido")

            tx_type = str(result.get("type", "")).lower()
            if tx_type not in VALID_TYPES:
                errors.append(f"Tipo inválido: {tx_type}")

            category = str(result.get("category", "")).strip()
            if not category or len(category) > 100:
                errors.append("Categoria inválida")

            description = str(result.get("description", "Automático")).strip()
            if len(description) > 255:
                description = description[:255]

            tx_date = result.get("date", today)

            if errors:
                logger.warning("LLM retornou dados inválidos: %s | raw: %s", errors, raw)
                return JsonResponse({"reply": f"Não foi possível registrar: {'; '.join(errors)}. Tente novamente."})

            Transaction.objects.create(
                user=request.user,
                description=description or "Automático",
                amount=amount,
                date=tx_date,
                category=category,
                type=tx_type,
            )

            logger.info("Transação criada via IA: user=%s type=%s amount=%s", request.user, tx_type, amount)
            ai_reply = f"Registrei: {tx_type.upper()} de R$ {amount} em {category}"
        else:
            ai_reply = result.get("reply", "Não entendi.")

        return JsonResponse({"reply": ai_reply})

    except json.JSONDecodeError:
        logger.error("LLM retornou JSON inválido: %s", raw)
        return JsonResponse({"reply": "Erro ao processar resposta do assistente."})
    except Exception as e:
        logger.exception("Erro no chat_api para usuário %s", request.user)
        return JsonResponse({"reply": "Ocorreu um erro interno. Tente novamente mais tarde."})
