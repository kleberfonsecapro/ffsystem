import os
import json
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from groq import Groq
from finance.models import Transaction

@login_required(login_url="/users/login/")
def chat_view(request):
    return render(request, "chat.html")

@login_required(login_url="/users/login/")
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método inválido"}, status=400)

    user_message = request.POST.get("message", "")
    today = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""
Você é SmartFinance AI, assistente financeiro.
Se reconhecer um registro financeiro (gasto/ganho), retorne JSON:
{{"is_transaction": true, "amount": 100.50, "date": "{today}",
 "category": "Alimentação", "type": "despesa", "description": "Comida"}}
Se NÃO for transação:
"is_transaction": false, "reply": "sua resposta"
"""

    try:
        client = Groq(api_key=os.environ.get("$"))

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)

        if result.get("is_transaction"):
            Transaction.objects.create(
                user=request.user,
                description=result.get("description", "Automático"),
                amount=result.get("amount"),
                date=result.get("date"),
                category=result.get("category"),
                type=result.get("type"),
            )
            ai_reply = f"Registrei: {result['type'].upper()} de R$ {result['amount']} em {result['category']}"
        else:
            ai_reply = result.get("reply", "Não entendi.")

        return JsonResponse({"reply": ai_reply})

    except Exception as e:
        return JsonResponse({"reply": f"Erro: {str(e)}"})
